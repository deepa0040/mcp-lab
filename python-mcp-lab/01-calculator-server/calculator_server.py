import math
from mcp.server.fastmcp import FastMCP

# Create the server and give it a name
mcp = FastMCP("calculator")


# ---------- TOOLS (actions the AI can call) ----------

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return a + b."""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a and return a - b."""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return a * b."""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b. Raises an error if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the given exponent."""
    return math.pow(base, exponent)


@mcp.tool()
def sqrt(x: float) -> float:
    """Return the square root of a non-negative number."""
    if x < 0:
        raise ValueError("Square root of a negative number is not supported.")
    return math.sqrt(x)


# ---------- RESOURCE (read-only data) ----------

@mcp.resource("calc://constants")
def constants() -> str:
    """Common math constants."""
    return f"pi = {math.pi}\ne = {math.e}\ntau = {math.tau}"


# ---------- PROMPT (reusable template) ----------

@mcp.prompt()
def explain_calculation(expression: str) -> str:
    """Ask the model to solve an expression step by step using the tools."""
    return (
        f"Solve this step by step: {expression}\n"
        "Use the calculator tools for every arithmetic operation "
        "and show each intermediate result."
    )


# ---------- START THE SERVER ----------

if __name__ == "__main__":
    mcp.run()