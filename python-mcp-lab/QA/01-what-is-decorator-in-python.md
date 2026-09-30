## What is a decorator in Python?

A **decorator** is a way to **add extra behavior to an existing function without changing the function's actual code**.

Think of it like **wrapping a gift**:

```text
Original function
      ↓
  [ Decorator ]
      ↓
Function with extra behavior
```

### 1. Normal function

```python
def greet():
    print("Hello!")

greet()
```

Output:

```text
Hello!
```

Now suppose you want to print `"Starting..."` before every function and `"Finished!"` afterward.

You could modify the function:

```python
def greet():
    print("Starting...")
    print("Hello!")
    print("Finished!")
```

But imagine you have **100 functions**. You don't want to modify all 100.

That's where a decorator helps.

---

## 2. Creating a decorator

```python
def my_decorator(func):

    def wrapper():
        print("Starting...")
        func()
        print("Finished!")

    return wrapper
```

Then:

```python
@my_decorator
def greet():
    print("Hello!")
```

And:

```python
greet()
```

Output:

```text
Starting...
Hello!
Finished!
```

### What does `@my_decorator` mean?

This:

```python
@my_decorator
def greet():
    print("Hello!")
```

is basically Python's shorter syntax for:

```python
def greet():
    print("Hello!")

greet = my_decorator(greet)
```

So the original `greet()` function gets **wrapped** by the decorator.

---

# Why are decorators useful?

They are useful when you want to apply the **same behavior to many functions**.

Common examples:

| Decorator use  | Purpose                            |
| -------------- | ---------------------------------- |
| Logging        | Log when a function runs           |
| Authentication | Check whether a user is authorized |
| Timing         | Measure execution time             |
| Caching        | Reuse previous results             |
| Validation     | Validate input                     |
| Retry          | Retry failed operations            |
| Permissions    | Check access before executing      |

---

# Very important for MCP

This is probably why you're encountering decorators while learning **MCP**.

You may see something like:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

Here:

```python
@mcp.tool()
```

is a **decorator**.

It tells the MCP framework:

> "Take this Python function and register it as an MCP tool."

So:

```python
def add(a, b):
    return a + b
```

is just a normal Python function.

But:

```python
@mcp.tool()
def add(a, b):
    return a + b
```

means:

```text
Python function
      ↓
   @mcp.tool()
      ↓
MCP recognizes/registers it
      ↓
AI can discover and call this tool
```

This is one of the important Python concepts to understand before going deeper into MCP.

### Simple way to remember

> **Decorator = a wrapper that adds behavior or tells a framework how to treat a function.**

And the `@` syntax is simply the convenient Python syntax for applying that decorator.
