"""Notes / Todo MCP server.

Tools: add_note, list_notes, search_notes, delete_note
Storage: SQLite (stdlib) in notes.db next to this file (override with NOTES_DB).

Run:  python server.py            (stdio transport)
"""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

DB_PATH = Path(os.environ.get("NOTES_DB", Path(__file__).with_name("notes.db")))

mcp = MCPServer("notes-todo")


# ---------------------------------------------------------------- storage --
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            body       TEXT NOT NULL DEFAULT '',
            kind       TEXT NOT NULL DEFAULT 'note',
            done       INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    return conn


class Note(TypedDict):
    """Shape returned to the client. MCP turns this into the tool's output schema."""

    id: int
    title: str
    body: str
    kind: str
    done: bool
    created_at: str


def _to_note(row: sqlite3.Row) -> Note:
    return Note(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        kind=row["kind"],
        done=bool(row["done"]),
        created_at=row["created_at"],
    )


# ------------------------------------------------------------------ tools --
# The function signature IS the tool schema:
#   - parameter names/types/defaults -> JSON Schema `inputSchema`
#   - docstring                      -> tool description the LLM reads
#   - return type                    -> `outputSchema` (structured output)
@mcp.tool()
def add_note(
    title: str,
    body: str = "",
    kind: Literal["note", "todo"] = "note",
) -> Note:
    """Create a new note or todo item.

    Args:
        title: Short headline for the note.
        body: Optional longer text.
        kind: "note" for plain notes, "todo" for tasks.
    """
    title = title.strip()
    if not title:
        raise ToolError("title must not be empty")

    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(_connect()) as conn, conn:  # `with conn` = commit/rollback
        cur = conn.execute(
            "INSERT INTO notes (title, body, kind, created_at) VALUES (?, ?, ?, ?)",
            (title, body, kind, created),
        )
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _to_note(row)


@mcp.tool()
def list_notes(
    kind: Literal["note", "todo", "all"] = "all",
    limit: int = 50,
) -> list[Note]:
    """List saved notes, newest first.

    Args:
        kind: Filter by type, or "all".
        limit: Maximum number of results (1-200).
    """
    limit = max(1, min(limit, 200))
    sql = "SELECT * FROM notes"
    params: list[object] = []
    if kind != "all":
        sql += " WHERE kind = ?"
        params.append(kind)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with closing(_connect()) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_to_note(r) for r in rows]


@mcp.tool()
def search_notes(query: str, limit: int = 20) -> list[Note]:
    """Search note titles and bodies (case-insensitive substring match).

    Args:
        query: Text to look for.
        limit: Maximum number of results (1-200).
    """
    limit = max(1, min(limit, 200))
    # Escape LIKE wildcards so the user's text is matched literally.
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{escaped}%"

    with closing(_connect()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM notes
            WHERE title LIKE ? ESCAPE '\\' OR body LIKE ? ESCAPE '\\'
            ORDER BY id DESC LIMIT ?
            """,
            (pattern, pattern, limit),
        ).fetchall()
    return [_to_note(r) for r in rows]


@mcp.tool()
def delete_note(note_id: int) -> str:
    """Delete a note by its id. Use list_notes or search_notes to find ids.

    Args:
        note_id: The id of the note to delete.
    """
    with closing(_connect()) as conn, conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if cur.rowcount == 0:
        raise ToolError(f"No note with id {note_id}. Use list_notes to see valid ids.")
    return f"Deleted note {note_id}"


if __name__ == "__main__":
    mcp.run()  # stdio by default