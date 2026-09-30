## Synchronous vs Asynchronous Tools in MCP

The easiest way to understand this is to first forget MCP for a moment and think about **how Python functions wait for work to finish**.

### 1. Synchronous = "Do this, then wait"

A synchronous function runs from start to finish before the program moves on.

```python
def add(a, b):
    return a + b
```

When you call:

```python
result = add(10, 20)
```

Python does:

```text
Call add()
    ↓
Calculate 10 + 20
    ↓
Wait until finished
    ↓
Return 30
    ↓
Continue
```

So:

> **Synchronous code blocks while the operation is running.**

---

# 2. Asynchronous = "Start this work, don't block unnecessarily"

An asynchronous function uses Python's `async`/`await` mechanism.

```python
async def get_data():
    result = await some_operation()
    return result
```

The important keywords are:

```python
async def
await
```

Conceptually:

```text
Start operation
      ↓
Is it waiting for I/O?
      ↓
Other work can run
      ↓
Operation finishes
      ↓
Continue
```

So:

> **Asynchronous code is useful when your program spends time waiting for I/O.**

---

# 3. The most important example: API calls

Suppose your MCP tool calls an external API.

```python
@mcp.tool()
def get_user():
    response = requests.get("https://api.example.com/user")
    return response.json()
```

Imagine the API takes **3 seconds**.

Your Python program essentially does:

```text
get_user()
   │
   ├── send request
   │
   ├── WAIT 3 seconds
   │
   └── return response
```

During that waiting period, synchronous code is blocked.

---

## Async version

You could use an async HTTP client:

```python
@mcp.tool()
async def get_user():
    response = await client.get("https://api.example.com/user")
    return response.json()
```

Now while waiting for the network response, the event loop can handle other asynchronous work.

Conceptually:

```text
get_user()
   │
   ├── send request
   │
   ├── waiting ─────────────┐
   │                        │
   │                 Other async work
   │                        │
   └──── response arrives ←─┘
```

---

# 4. Why does this matter in MCP?

Imagine your MCP server has three tools:

```text
MCP Server
│
├── get_weather()
├── get_github_status()
└── get_database_data()
```

Suppose all three need to make network requests.

### Synchronous

If each takes 3 seconds:

```text
get_weather()
    ↓ 3 sec

get_github_status()
    ↓ 3 sec

get_database_data()
    ↓ 3 sec

Total ≈ 9 sec
```

The operations are handled sequentially.

### Asynchronous

If the operations can run concurrently:

```text
get_weather()       ─────── 3 sec ───────┐
get_github_status() ─────── 3 sec ───────┤
get_database_data() ─────── 3 sec ───────┘

Total ≈ 3 sec
```

This is the major benefit of asynchronous programming for **I/O-bound workloads**.

---

# 5. Very important: Async does NOT mean "faster Python"

This is a common beginner misunderstanding.

Suppose:

```python
def calculate():
    for i in range(1_000_000_000):
        ...
```

Making it:

```python
async def calculate():
    ...
```

doesn't magically make the calculation faster.

Async is primarily useful when your program is **waiting** for things such as:

* HTTP APIs
* databases
* files
* network services
* other external systems

Think:

```text
CPU work
    → async usually isn't the solution

Waiting for external system
    → async can be very useful
```

---

# 6. Simple analogy

Imagine you work at a restaurant.

### Synchronous

You:

```text
Take order
   ↓
Give order to kitchen
   ↓
STAND in kitchen waiting
   ↓
Food ready
   ↓
Give food to customer
   ↓
Take next order
```

You're wasting time while waiting.

### Asynchronous

You:

```text
Take order #1
   ↓
Give to kitchen
   ↓
Take order #2
   ↓
Give to kitchen
   ↓
Take order #3
   ↓
Food #1 ready
   ↓
Serve #1
```

You use the waiting time productively.

That's roughly the idea behind asynchronous I/O.

---

# 7. `async` and `await`

These two keywords work together.

### `async def`

Defines an asynchronous function:

```python
async def get_data():
    ...
```

### `await`

Waits for an asynchronous operation:

```python
result = await get_data_from_api()
```

The key idea is:

```text
async def
    ↓
"This function can perform async operations"

await
    ↓
"Wait for this operation, but allow the event loop
to handle other async work"
```

---

# 8. MCP example

### Synchronous MCP tool

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

This is perfectly fine.

There's no meaningful waiting involved.

---

### Asynchronous MCP tool

Imagine the tool calls an API:

```python
@mcp.tool()
async def get_weather(city: str):
    """Get weather information."""
    
    response = await get_weather_from_api(city)

    return response
```

Here async makes sense because the tool is waiting for an external service.

---

# 9. Don't make everything async

You don't need to write:

```python
async def add(...)
```

just because you're building an MCP server.

For a simple calculation:

```python
@mcp.tool()
def add(a: int, b: int):
    return a + b
```

is appropriate.

For an API/database/network operation:

```python
@mcp.tool()
async def get_data():
    ...
```

may be appropriate.

---

# 10. Quick comparison

|                    | Synchronous              | Asynchronous                    |
| ------------------ | ------------------------ | ------------------------------- |
| Syntax             | `def`                    | `async def`                     |
| Waiting            | Blocks current execution | Can yield control while waiting |
| Keyword            | —                        | `await`                         |
| Simple calculation | Good                     | Usually unnecessary             |
| API calls          | Can work                 | Often useful                    |
| Database calls     | Can work                 | Often useful                    |
| Network I/O        | Can work                 | Often useful                    |
| Concurrent I/O     | More difficult           | Easier                          |
| Complexity         | Simpler                  | More complex                    |

---

## 11. One important correction to remember

Don't think:

> **Synchronous = slow, asynchronous = fast**

That's not correct.

Think:

> **Synchronous = execute and wait before continuing.**

> **Asynchronous = when waiting on async I/O, allow other async work to proceed.**

For MCP, your decision can usually start with this question:

```text
Does my tool mostly calculate/process something?
        │
        ├── YES → synchronous is often enough
        │
        └── NO
             │
             ▼
Does it wait for API/database/network I/O?
             │
             └── YES → consider asynchronous
```

