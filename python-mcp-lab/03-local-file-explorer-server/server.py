"""
Read-only local file explorer MCP server.

Install:  pip install "mcp[cli]>=2,<3"   (mcp 2.x; for 1.x see README)
Run:      python file_explorer_server.py /path/to/root
Inspect:  mcp dev file_explorer_server.py -- /path/to/root   (opens MCP Inspector)

Concepts demonstrated
- TOOLS     : model-controlled actions with arguments (list_dir, read_file, search_files)
- RESOURCES : application-controlled data the client can browse/attach (file:// URIs)
- SAFETY    : every path goes through safe_path(), which confines access to ROOT
"""

import os
import sys
from fnmatch import fnmatch
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.resources import FunctionResource

# --------------------------------------------------------------------------
# Config: a single root folder. Nothing outside it is ever touched.
# --------------------------------------------------------------------------
def _pick_root() -> Path:
    """Root priority: EXPLORER_ROOT env var > argv[1] (if a real directory) > cwd.

    Under `mcp dev`, sys.argv belongs to the mcp CLI (argv[1] == "dev"), so we
    must not blindly trust it.
    """
    env = os.environ.get("EXPLORER_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    if len(sys.argv) > 1 and Path(sys.argv[1]).expanduser().is_dir():
        return Path(sys.argv[1]).expanduser().resolve()
    return Path(".").resolve()


ROOT = _pick_root()

if not ROOT.is_dir():
    sys.exit(f"Root is not a directory: {ROOT}")

MAX_READ_BYTES = 200_000       # cap for read_file / resources
MAX_SEARCH_FILE_BYTES = 1_000_000
MAX_LIST_ENTRIES = 500
MAX_RESOURCES = 500            # cap on files advertised as resources
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".idea"}

mcp = MCPServer("local-file-explorer")


# --------------------------------------------------------------------------
# Path safety
# --------------------------------------------------------------------------
def safe_path(rel: str = ".") -> Path:
    """Resolve `rel` against ROOT and make sure the result stays inside ROOT.

    - Rejects absolute paths.
    - .resolve() collapses `..` AND follows symlinks, so both `../../etc/passwd`
      and a symlink pointing outside ROOT end up outside ROOT and get rejected.
    """
    if os.path.isabs(rel):
        raise ValueError("Absolute paths are not allowed; use a path relative to the root.")
    candidate = (ROOT / rel).resolve()
    if not candidate.is_relative_to(ROOT):
        raise ValueError("Path escapes the allowed root folder.")
    return candidate


def _read_text(path: Path, max_bytes: int = MAX_READ_BYTES) -> str:
    with open(path, "rb") as f:
        data = f.read(max_bytes + 1)
    if b"\0" in data[:8192]:
        raise ValueError("File looks binary; refusing to read it as text.")
    truncated = len(data) > max_bytes
    text = data[:max_bytes].decode("utf-8", errors="replace")
    if truncated:
        text += f"\n\n[... truncated at {max_bytes} bytes ...]"
    return text


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix() or "."


# --------------------------------------------------------------------------
# TOOLS
# --------------------------------------------------------------------------
@mcp.tool()
def list_dir(path: str = ".") -> str:
    """List files and folders in a directory (relative to the root)."""
    target = safe_path(path)
    if not target.is_dir():
        raise ValueError(f"Not a directory: {path}")

    entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    lines = []
    for p in entries[:MAX_LIST_ENTRIES]:
        if p.is_dir():
            lines.append(f"[dir]  {p.name}/")
        else:
            try:
                lines.append(f"[file] {p.name}  ({p.stat().st_size} bytes)")
            except OSError:
                lines.append(f"[file] {p.name}")
    if len(entries) > MAX_LIST_ENTRIES:
        lines.append(f"... {len(entries) - MAX_LIST_ENTRIES} more entries not shown")
    return "\n".join(lines) or "(empty directory)"


@mcp.tool()
def read_file(path: str, max_bytes: int = MAX_READ_BYTES) -> str:
    """Read a text file (relative to the root). Large files are truncated."""
    target = safe_path(path)
    if not target.is_file():
        raise ValueError(f"Not a file: {path}")
    return _read_text(target, min(max_bytes, MAX_READ_BYTES))


@mcp.tool()
def search_files(
    query: str,
    path: str = ".",
    glob: str = "*",
    max_results: int = 50,
) -> str:
    """Case-insensitive search for `query` in file names and file contents.

    Args:
        query: text to look for.
        path: subdirectory to search in (relative to the root).
        glob: only consider files whose name matches, e.g. "*.py".
        max_results: stop after this many hits.
    """
    if not query:
        raise ValueError("query must not be empty")
    start = safe_path(path)
    if not start.is_dir():
        raise ValueError(f"Not a directory: {path}")

    q = query.lower()
    hits: list[str] = []

    for dirpath, dirnames, filenames in os.walk(start):  # followlinks=False
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not fnmatch(name, glob):
                continue
            fpath = Path(dirpath) / name
            # Symlinked files may point outside ROOT -> re-check every file.
            try:
                real = fpath.resolve()
                if not real.is_relative_to(ROOT) or not real.is_file():
                    continue
            except OSError:
                continue

            rel = _rel(real)
            if q in name.lower():
                hits.append(f"{rel}  (name match)")
            try:
                if real.stat().st_size > MAX_SEARCH_FILE_BYTES:
                    continue
                text = _read_text(real, MAX_SEARCH_FILE_BYTES)
            except (ValueError, OSError):
                continue  # binary or unreadable
            for lineno, line in enumerate(text.splitlines(), 1):
                if q in line.lower():
                    hits.append(f"{rel}:{lineno}: {line.strip()[:200]}")
                    if len(hits) >= max_results:
                        return "\n".join(hits) + "\n[max_results reached]"
            if len(hits) >= max_results:
                return "\n".join(hits) + "\n[max_results reached]"

    return "\n".join(hits) or "No matches."


# --------------------------------------------------------------------------
# RESOURCES: expose files under ROOT as file:// URIs.
#
# Tools are things the *model* decides to call. Resources are data the
# *client/app* lists and attaches as context (think: a file picker).
# We register one static resource per file (capped). A dynamic alternative is
# a resource template like @mcp.resource("file://{path}"), but template
# params match a single path segment, so static registration is simpler here.
# --------------------------------------------------------------------------
def _register_resources() -> None:
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            fpath = Path(dirpath) / name
            try:
                real = fpath.resolve()
                if not real.is_relative_to(ROOT) or real.stat().st_size > MAX_READ_BYTES:
                    continue
                with open(real, "rb") as f:
                    if b"\0" in f.read(8192):
                        continue  # skip binary files
            except OSError:
                continue

            mcp.add_resource(
                FunctionResource(
                    uri=real.as_uri(),  # file:///abs/path/to/file
                    name=_rel(real),
                    description=f"File: {_rel(real)}",
                    mime_type="text/plain",
                    fn=lambda p=real: _read_text(p),
                )
            )
            count += 1
            if count >= MAX_RESOURCES:
                return


_register_resources()

if __name__ == "__main__":
    mcp.run()  # stdio transport