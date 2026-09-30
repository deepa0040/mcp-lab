# UV in Python — Quick Notes

## 1. What is `uv`?

**`uv` is a fast Python package and project manager** built by Astral.

It can help with:

* Python versions
* Virtual environments
* Installing packages
* Managing project dependencies
* Running Python code
* Locking dependencies

Think of it as a modern tool that can handle tasks traditionally done with:

```text
pip + venv + requirements.txt + python
```

---

## 2. Why use `uv`?

Without `uv`, you might do:

```bash
python -m venv .venv
source .venv/bin/activate
pip install mcp
python main.py
```

With `uv`:

```bash
uv venv
uv add mcp
uv run main.py
```

So `uv` simplifies Python project setup and dependency management.

---

# 3. Installing `uv`

On Linux / WSL:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then reload your shell:

```bash
source ~/.bashrc
```

After installing `uv`, verify it:

```bash
uv --version
```

Example:

```text
uv 0.x.x
```
Note: You don't normally install **uv** using **pip install uv**. It is a standalone tool.
---

# 4. Create a Python project

```bash
uv init my-project
```

This creates a project structure such as:

```text
my-project/
├── pyproject.toml
├── README.md
└── main.py
```

Then:

```bash
cd my-project
```

---

# 5. Create a virtual environment

```bash
uv venv
```

This creates:

```text
.venv/
```

A virtual environment isolates your project's Python packages from other projects.

For example:

```text
Project A
  └── .venv
       └── mcp 1.x

Project B
  └── .venv
       └── mcp 2.x
```

This is especially useful for your MCP projects because different tutorials may require different MCP SDK versions.

---

# 6. Add a package

```bash
uv add mcp
```

This means:

> Add the `mcp` Python package to my project.

For example:

```bash
uv add requests
uv add flask
uv add pytest
```

You can add multiple packages:

```bash
uv add mcp pytest requests
```

`uv` updates the project's dependency information in `pyproject.toml`.

---

# 7. Install a specific version

This is important when working with tutorials.

```bash
uv add "mcp<2"
```

or:

```bash
uv add "mcp==1.12.4"
```

You can therefore control which version your project uses.

For your previous MCP problem:

```text
Code expects → MCP v1
Installed    → MCP v2
```

You could use:

```bash
uv add "mcp<2"
```

instead of installing packages globally.

---

# 8. Run Python with `uv`

Instead of:

```bash
python main.py
```

you can use:

```bash
uv run main.py
```

`uv` runs the program using the project's environment and dependencies.

You can also run:

```bash
uv run python test_main1.py
```

or:

```bash
uv run pytest
```

---

# 9. `pyproject.toml`

This is an important file in a modern Python project.

Example:

```toml
[project]
name = "mcp-calculator"
version = "0.1.0"

dependencies = [
    "mcp<2",
]
```

It describes your project and its dependencies.

Think of it as:

> **Project configuration + dependency declaration**

---

# 10. `uv.lock`

When you use `uv`, you'll typically also see:

```text
uv.lock
```

This records the exact dependency versions selected for the project.

For example:

```text
pyproject.toml
      ↓
"What dependencies do I need?"

uv.lock
      ↓
"What exact versions did this project resolve?"
```

This helps make the environment reproducible.

For example:

```text
Developer A
      ↓
uv sync
      ↓
same dependency versions

Developer B
      ↓
uv sync
      ↓
same dependency versions
```

---

# 11. `uv sync`

```bash
uv sync
```

This synchronizes your environment with the project's declared dependencies and lockfile.

Useful when you clone someone else's project:

```bash
git clone <repository>
cd project
uv sync
```

Then:

```bash
uv run main.py
```

---

# 12. `uv add` vs `uv pip install`

You'll see both commands, but they have different purposes.

### `uv add`

```bash
uv add mcp
```

Used for a **project**.

It updates the project dependency configuration.

### `uv pip install`

```bash
uv pip install mcp
```

Acts more like traditional `pip`.

It is useful when you specifically want pip-style package installation.

For a new project, you'll generally want:

```bash
uv add <package>
```

rather than manually installing everything with `uv pip`.

---

# 13. Useful commands

| Command               | Purpose                            |
| --------------------- | ---------------------------------- |
| `uv --version`        | Check uv version                   |
| `uv init`             | Create Python project              |
| `uv venv`             | Create virtual environment         |
| `uv add <package>`    | Add dependency                     |
| `uv remove <package>` | Remove dependency                  |
| `uv run <command>`    | Run command in project environment |
| `uv sync`             | Synchronize environment            |
| `uv lock`             | Update/create lockfile             |
| `uv tree`             | View dependency tree               |
| `uv python list`      | List available Python versions     |

---

# 14. Typical MCP project

For your MCP learning, you could use:

```bash
uv init mcp-calculator
cd mcp-calculator

uv add "mcp<2"

uv run server.py
```

Project:

```text
mcp-calculator/
│
├── .venv/
├── pyproject.toml
├── uv.lock
├── server.py
└── test_main.py
```

The relationship is:

```text
                MCP Calculator
                      │
                      ↓
               Python project
                      │
                      ↓
                     uv
             ┌────────┼────────┐
             ↓        ↓        ↓
          .venv   pyproject  uv.lock
             │       .toml
             ↓
          MCP SDK
             │
             ↓
        server.py
```

---

## 15. `uv` vs `pip` 

| Tool  | Ecosystem          | Main purpose                               |
| ----- | ------------------ | ------------------------------------------ |
| `uv`  | Python             | Project + package + environment management |
| `pip` | Python             | Package installation                       |

So for your current learning:

```text
Python MCP
   ↓
  uv
   ↓
 MCP Python SDK
   ↓
 server.py
```

### One-line definition

> **uv is a fast Python package and project manager used to create environments, manage dependencies, resolve/lock versions, and run Python projects.**
