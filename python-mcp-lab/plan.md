# Python MCP starter projects

Ordered from easiest to hardest. Each one teaches something new, and all of them are useful on their own.

## Beginner

**1. Notes / Todo server**
- Tools: `add_note`, `list_notes`, `search_notes`, `delete_note`
- Storage: a local JSON file or SQLite
- Learn: tool schemas, type hints, basic persistence

**2. Local file explorer (read-only)**
- Tools: `list_dir`, `read_file`, `search_files`
- Resources: expose files as `file://` resources
- Learn: resources vs tools, path safety (block `../` escapes, restrict to one root folder)

**3. Weather / currency / news lookup**
- Wrap one free public API (Open-Meteo needs no API key)
- Learn: async tools with `httpx`, error handling, timeouts

## Intermediate

**4. SQLite database explorer**
- Tools: `list_tables`, `describe_table`, `run_select_query`
- Enforce read-only (reject anything but `SELECT`)
- Learn: input validation, least privilege, why "natural language to SQL" needs guardrails

**5. GitHub issues assistant**
- Tools: `search_issues`, `get_issue`, `create_issue_comment`
- Learn: API auth with tokens from env vars, pagination, separating read and write tools, prompt injection risk from issue text

**6. Personal expense tracker**
- Tools: `log_expense`, `monthly_summary`, `spending_by_category`
- Prompts: a "monthly review" prompt template
- Learn: using all three MCP primitives (tools, resources, prompts)

## Advanced

**7. Document Q&A (RAG) server**
- Tools: `index_folder`, `semantic_search`
- Stack: embeddings plus a vector store like Chroma or FAISS
- Learn: long-running tasks, progress reporting, returning citations

**8. Ops Assistant (capstone)**
- Combines a database, ticketing, and metrics
- Learn: Streamable HTTP, OAuth, Docker, logging, tests, deployment

## Suggested path

Start with **#1**, then **#4**, then **#5**. You'll cover the basics, safe data access, and external APIs with auth. After that you'll be ready to move to remote deployment.

## Tips for all of them

- Write clear docstrings; the model reads them to decide when to call a tool.
- Return concise, structured output rather than huge dumps.
- Test with the MCP Inspector before connecting to Claude.

Want me to scaffold project #1 with full working code so you can run it today?