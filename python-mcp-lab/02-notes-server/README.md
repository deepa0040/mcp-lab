# Notes / Todo MCP Server 

## 1. What is this project?

This is a small program that lets an AI (like Claude) **save, list, search, and delete your notes**.

You don't click buttons. You just say *"Add a todo to buy milk"* and the AI calls your Python code to do it.

The technology that makes this possible is called **MCP**.

## 2. What is MCP? 

**MCP (Model Context Protocol)** is a standard way for an AI to use *tools* that you write.

Think of it like a restaurant:

| Restaurant | MCP |
|---|---|
| Customer | The AI (Claude) |
| Waiter | The MCP protocol |
| Kitchen | **Your Python server** (`server.py`) |
| Menu | The list of tools + what inputs they need |

The AI reads the "menu" (your tool descriptions), decides what to order, and your code does the actual work.

```
  You: "Add a todo: buy milk"
        |
        v
  +-----------+   asks to call add_note(...)   +--------------+
  |    AI     | -----------------------------> | server.py    |
  |  (Claude) | <----------------------------- | (your code)  |
  +-----------+   returns the saved note       +------+-------+
                                                      |
                                                      v
                                                  notes.db
                                              (SQLite database)
```

In this project you build the **right-hand side**: the server.

## 3. The files

| File | What it is |
|---|---|
| `server.py` | **The main project.** Defines the 4 tools and saves data to a database. |
| `test_client.py` | A fake "AI" that calls your tools so you can check they work. Not part of the server itself. |
| `notes.db` | Created automatically the first time you add a note. This is where notes are stored. |

## 4. Setup and run

```bash
pip install "mcp[cli]"      # install the MCP library
python test_client.py       # run the test
```

If you see the four tools listed and notes being added, searched and deleted, it works.

To poke at the tools yourself in a browser:

```bash
mcp dev server.py
```

## 5. How `server.py` works, piece by piece

The file has 3 parts: **setup**, **storage helpers**, and **tools**.

### Part A: Setup

```python
mcp = MCPServer("notes-todo")
```

This creates your server and names it. Every tool gets attached to this object.

```python
DB_PATH = Path(os.environ.get("NOTES_DB", Path(__file__).with_name("notes.db")))
```

This decides where the database file lives: next to `server.py`, unless you set an environment variable called `NOTES_DB`. (The test script uses that to avoid touching your real notes.)

### Part B: Storage helpers

**`_connect()`** opens the SQLite database and creates the `notes` table if it doesn't exist yet. The table has these columns:

| Column | Meaning |
|---|---|
| `id` | Unique number, assigned automatically (1, 2, 3...) |
| `title` | Short headline |
| `body` | Longer text (optional) |
| `kind` | Either `"note"` or `"todo"` |
| `done` | 0 or 1 (unused for now, ready for a future "complete" tool) |
| `created_at` | When it was saved |

**`Note`** is a *type description* of what a saved note looks like when sent back to the AI:

```python
class Note(TypedDict):
    id: int
    title: str
    ...
```

**`_to_note(row)`** converts a raw database row into that `Note` shape (it also turns `done` from `0/1` into `False/True`).

The leading underscore (`_connect`, `_to_note`) is a Python habit meaning "internal helper, not a tool".

### Part C: The tools

A tool is just a normal Python function with `@mcp.tool()` above it:

```python
@mcp.tool()
def add_note(title: str, body: str = "", kind: Literal["note", "todo"] = "note") -> Note:
    """Create a new note or todo item."""
```

That one line is where the magic happens. MCP reads your function and automatically builds the "menu entry" the AI sees:

| In your code | What MCP does with it |
|---|---|
| Function name `add_note` | Tool name |
| Docstring `"""Create a new note..."""` | Description the AI reads to decide *when* to use it |
| `title: str` (no default) | Required input, must be text |
| `body: str = ""` | Optional input, defaults to empty |
| `Literal["note", "todo"]` | Only these two values are allowed |
| `-> Note` | Shape of what comes back |

This is why type hints matter here. **You never write the schema by hand. Your type hints are the schema.** (You saw this in the test output: the big `add_noteArguments` block was generated from that one function signature.)

Now each tool:

| Tool | What it does | Notable detail |
|---|---|---|
| `add_note` | Inserts a row, returns the saved note | Rejects an empty title |
| `list_notes` | Returns notes newest first | Optional `kind` filter and `limit` |
| `search_notes` | Finds notes whose title or body contains your text | Uses SQL `LIKE`; special characters are escaped so `%` is searched literally |
| `delete_note` | Deletes by id | Errors if the id doesn't exist |

### Database details you'll see in the code

- **`?` placeholders**: `"... WHERE id = ?", (note_id,)` passes values separately from the SQL text. This prevents *SQL injection* (someone sneaking commands in through input). Always do this instead of building SQL with f-strings.
- **`with conn:`** means "save everything if the block succeeds, undo it if there's an error."
- **`closing(_connect())`** makes sure the database connection is closed afterwards.

### Errors: `ToolError`

```python
raise ToolError(f"No note with id {note_id}. Use list_notes to see valid ids.")
```

When something goes wrong in a way you expected (like a bad id), raise `ToolError`. Its message is sent back to the AI so it can understand and try again. Other kinds of exceptions are treated as crashes and hidden behind a generic message.

### The last two lines

```python
if __name__ == "__main__":
    mcp.run()
```

This starts the server. It talks over **stdio** (standard input/output): the AI app launches `server.py` as a subprocess and they exchange messages through it.

> **Important rule:** never use `print()` in this file. stdout is the channel the protocol uses, so a stray `print` corrupts the conversation. Use `logging` instead (it goes to stderr).

## 6. What `test_client.py` does

It acts like a tiny AI:

1. Launches `server.py` as a subprocess (using a temporary database).
2. Asks "what tools do you have?" (`list_tools`).
3. Calls each tool with sample inputs (`call_tool`).
4. Deliberately calls two things wrong (deleting id 999, using `kind="banana"`) to show that errors come back cleanly.

The `INFO ... failed` lines in the output are the server logging those two *intentional* mistakes. They are not bugs.

## 7. Use it with a real AI (Claude Desktop)

Open `claude_desktop_config.json` and add (use full absolute paths):

```json
{
  "mcpServers": {
    "notes-todo": {
      "command": "python",
      "args": ["/full/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop, then try:

- *"Add a todo to buy milk"*
- *"Show all my todos"*
- *"Search my notes for milk"*
- *"Delete note 1"*

If `python` isn't found, put the full path to your Python (or your virtualenv's Python) in `command`.

## 8. Mini glossary

| Term | Meaning |
|---|---|
| **MCP** | Standard protocol for AI apps to call your tools |
| **Server** | Your program (`server.py`) that provides tools |
| **Client** | The thing that calls the tools (Claude, or `test_client.py`) |
| **Tool** | A Python function the AI is allowed to call |
| **Schema** | A description of a tool's inputs/outputs (auto-generated from type hints) |
| **stdio** | Communication via a subprocess's input/output streams |
| **SQLite** | A database stored in a single file, built into Python |
| **Decorator** (`@mcp.tool()`) | A line above a function that registers/modifies it |

## 9. Things to try (in order of difficulty)

1. **Change a docstring** and re-run `mcp dev server.py`. See the tool description change.
2. **Add a `priority` field** (`"low" | "high"`) to `add_note` using `Literal`. Watch the schema update by itself.
3. **Write `complete_note(note_id)`** that sets `done = 1`. The column already exists.
4. **Add a `count_notes` tool** that returns a single number.

## 10. Version note

This project uses **mcp 2.x** (`from mcp.server.mcpserver import MCPServer`).
Older tutorials use mcp 1.x, where it is `from mcp.server.fastmcp import FastMCP`.
The `@mcp.tool()` idea is identical. Only the import names differ.