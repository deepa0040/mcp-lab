# MCP Testing — Manual & Automated

Testing an MCP server means verifying that the server starts correctly, exposes the expected MCP capabilities, accepts valid inputs, returns correct results, and handles errors properly.

There are two main approaches:

1. **Manual Testing** → MCP Inspector
2. **Automated Testing** → Python tests + pytest + CI/CD

---

## 1. MCP Testing Overview

```text
                         MCP Testing
                              │
                 ┌────────────┴────────────┐
                 │                         │
             Manual Testing          Automated Testing
                 │                         │
          MCP Inspector             pytest / test code
                 │                         │
        Developer interacts          Runs automatically
        with MCP server              in local/CI
```

---

# 2. Manual Testing

## What is Manual Testing?

Manual testing means a developer interacts with the MCP server and verifies its behavior manually.

The commonly used tool is:

**MCP Inspector**

It provides an interface for connecting to an MCP server and inspecting its capabilities.

```text
Developer
    │
    ▼
MCP Inspector
    │
    ▼
MCP Server
    │
    ▼
Tools / Resources / Prompts
```

---

## 3. MCP Inspector

MCP Inspector is a development and debugging tool for MCP servers.

It can be used to inspect:

* Tools
* Tool schemas
* Tool arguments
* Tool execution
* Tool responses
* Resources
* Prompts
* Errors
* Server connectivity

---

## 4. Start MCP Inspector

A common way to start Inspector is:

```bash
npx @modelcontextprotocol/inspector
```

The exact connection configuration depends on how your MCP server is being run.

For a Python MCP server using `uv`, your server may be started with:

```bash
uv run main.py
```

or configured through Inspector to launch the server.

---

# 5. Example Python MCP Server

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

The server exposes:

```text
Tools
├── add
└── multiply
```

---

# 6. Testing with MCP Inspector

After connecting the server to Inspector:

```text
Inspector
   │
   ├── Discover server
   │
   ├── List tools
   │
   ├── Select "add"
   │
   ├── Enter:
   │      a = 10
   │      b = 20
   │
   ├── Execute
   │
   └── Verify:
          30
```

### Things to verify

| Test              | Expected              |
| ----------------- | --------------------- |
| Server connection | Successful            |
| `add` tool        | Visible               |
| `multiply` tool   | Visible               |
| Tool arguments    | Correct schema        |
| `add(10,20)`      | `30`                  |
| `multiply(5,4)`   | `20`                  |
| Invalid input     | Appropriate error     |
| Unknown tool      | Appropriate MCP error |

---

# 7. Advantages of Manual Testing

Manual testing is useful during development because it allows you to quickly:

* Explore a new MCP server
* Verify that tools are registered
* Test different inputs
* Inspect responses
* Debug errors
* Understand MCP behavior
* Verify the server before writing automated tests

### Limitation

Manual testing depends on a developer.

For example:

```text
Developer
   ↓
Open Inspector
   ↓
Enter input
   ↓
Click tool
   ↓
Check result
```

If you have 50 test cases, manually repeating this process becomes inefficient.

This is where automated testing is useful.

---

# 8. Automated Testing

Automated testing means writing test code that verifies MCP server behavior without requiring a developer to manually interact with Inspector.

A typical Python stack is:

```text
Python MCP Server
       │
       ▼
Python Test Code
       │
       ▼
pytest
       │
       ▼
CI/CD
```

---

# 9. Testing Levels

MCP projects can use multiple testing levels.

```text
                    MCP Tests
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
      Unit         Integration         E2E
      Tests           Tests            Tests
        │               │               │
        ▼               ▼               ▼
   Python logic     MCP protocol     Whole system
```

---

# 10. Unit Testing

Unit tests test the underlying Python logic.

Example:

```python
def add(a, b):
    return a + b


def test_add():
    assert add(2, 3) == 5
```

Run:

```bash
pytest
```

Expected:

```text
1 passed
```

### What does this test?

```text
Python function
      ↓
add(2, 3)
      ↓
5
```

It does **not** verify the complete MCP communication path.

---

# 11. MCP Integration Testing

Integration testing verifies that the MCP interface works correctly.

Conceptually:

```text
Test
 │
 ▼
MCP Client
 │
 │ MCP request
 ▼
MCP Server
 │
 ▼
Tool
 │
 ▼
Result
```

For example, an integration test should verify that:

```text
Tool: add

Input:
{
    "a": 10,
    "b": 20
}

Result:
30
```

This checks more than the underlying Python function.

It helps verify:

* MCP server startup
* Tool registration
* MCP communication
* Tool name
* Input schema
* Tool execution
* Returned result

The exact Python testing API depends on the MCP SDK version being used, so integration tests should follow the API provided by the installed SDK version.

---

# 12. Error Testing

Automated tests should also verify failures.

Example:

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")

    return a / b
```

Test:

```python
import pytest


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)
```

This verifies that the expected error occurs.

---

# 13. What Should We Test?

A useful MCP test suite can cover:

### Server

```text
✓ Server starts
✓ Server connects
✓ Expected capabilities are available
```

### Tools

```text
✓ Tool exists
✓ Tool name is correct
✓ Tool schema is correct
✓ Required parameters are present
✓ Valid input works
✓ Invalid input is handled
✓ Tool returns expected result
```

### Resources

```text
✓ Resource exists
✓ Resource can be read
✓ Invalid resource is handled
```

### Prompts

```text
✓ Prompt exists
✓ Required arguments are accepted
✓ Expected prompt content is returned
```

### Errors

```text
✓ Invalid input
✓ Missing parameters
✓ Unknown tool
✓ Tool execution failure
✓ External dependency failure
```

---

# 14. Automated Testing with pytest

Install pytest in a `uv` project:

```bash
uv add --dev pytest
```

Run tests:

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

Example:

```text
tests/
├── test_calculator.py
├── test_tools.py
└── test_mcp_server.py
```

---

# 15. Test Naming

Use descriptive test names.

Good:

```python
def test_add_returns_sum():
    ...


def test_divide_by_zero_returns_error():
    ...


def test_calculator_exposes_add_tool():
    ...
```

Avoid:

```python
def test_1():
    ...


def test_tool():
    ...
```

A good test name should explain what behavior is being verified.

---

# 16. CI/CD Automation

Once tests work locally, run them automatically in CI.

Example GitHub Actions workflow:

```yaml
name: MCP Tests

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest
```

The workflow becomes:

```text
Developer
    │
    │ git push
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── Install uv
    │
    ├── Install dependencies
    │
    ├── Run pytest
    │
    └── PASS / FAIL
```

---

# 17. Manual vs Automated Testing

| Feature              | Manual                | Automated                  |
| -------------------- | --------------------- | -------------------------- |
| Main tool            | MCP Inspector         | pytest                     |
| Human interaction    | Required              | Not required               |
| Best for             | Exploration/debugging | Regression testing         |
| Tool testing         | Yes                   | Yes                        |
| Schema inspection    | Yes                   | Yes                        |
| Repeatability        | Low                   | High                       |
| CI/CD                | Not ideal             | Yes                        |
| Fast experimentation | Excellent             | Moderate                   |
| Large test suite     | Difficult             | Suitable                   |
| Debugging new server | Excellent             | Useful after initial setup |

---

# 18. MCP Inspector vs pytest

They are not competing tools.

They solve different problems.

```text
                  MCP Development
                        │
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
    MCP Inspector                 pytest
           │                         │
       Manual                    Automated
           │                         │
    Explore/debug             Verify/regression
           │                         │
           └────────────┬────────────┘
                        ▼
                   MCP Server
```

### Inspector

Use when you are asking:

> "What does my MCP server expose, and does this tool work?"

### Automated tests

Use when you are asking:

> "Does my MCP server continue to work correctly every time I change the code?"

---

# 19. Recommended MCP Development Workflow

For a new Python MCP project:

```text
1. Write MCP server
        ↓
2. Run locally
        ↓
3. Connect MCP Inspector
        ↓
4. Manually test tools
        ↓
5. Fix issues
        ↓
6. Write unit tests
        ↓
7. Write MCP integration tests
        ↓
8. Run pytest
        ↓
9. Add GitHub Actions
        ↓
10. Run tests automatically on every push/PR
```

---

# 20. Example Project Structure

```text
mcp-calculator/
│
├── src/
│   └── server.py
│
├── tests/
│   ├── test_calculator.py
│   ├── test_tools.py
│   └── test_mcp_server.py
│
├── .github/
│   └── workflows/
│       └── test.yml
│
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 21. Quick Commands

### Start Python MCP server

```bash
uv run main.py
```

### Start MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

### Install pytest

```bash
uv add --dev pytest
```

### Run tests

```bash
uv run pytest
```

### Run verbose tests

```bash
uv run pytest -v
```

---

# 22. Key Takeaways

```text
MCP Testing
│
├── Manual Testing
│   └── MCP Inspector
│       ├── Discover tools
│       ├── Inspect schemas
│       ├── Execute tools
│       └── Debug responses/errors
│
└── Automated Testing
    └── pytest
        ├── Unit tests
        ├── MCP integration tests
        ├── Error tests
        └── CI/CD regression tests
```

### Remember

> **MCP Inspector = manually inspect and debug.**

> **pytest = automatically verify behavior.**

> **GitHub Actions = automatically run those tests whenever code changes.**

The practical goal is to use **Inspector while developing** and **automated tests in CI/CD** so that MCP changes can be validated repeatedly without manual testing.
