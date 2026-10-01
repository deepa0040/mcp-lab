# Python Concept

## Literals in Python
A literal is a value that you write directly in your code. It's not a variable, and it's not calculated. It's just the raw value itself, exactly as it appears.

Think of it like this: if a variable is a labeled box, the literal is the thing you put inside the box.
```bash
age = 25
```
Here, `age` is the variable (the box), and `25` is the literal (the value inside).


## Hints in python
A type hint is a **note you add to your code** that says what kind of value a variable or function should hold.

Think of it like writing a label on a box: "This box is for numbers only."

The important part: **Python does not enforce it**. It's just a helpful note for you, other programmers, and your editor.

**Example: Hints for variables**

```bash
name: str = "Ravi"
age: int = 25
height: float = 5.9
is_student: bool = True
```

**Example: Hints for functions**
```bash
def add(a: int, b: int) -> int:
    return a + b
```
- a: int and b: int mean the inputs should be integers
- -> int means the function returns an integer

```bash
def say_hi() -> None:
    print("Hi")
```

## Docstrings in Python
A docstring is a **piece of text that explains what your code does**. You write it inside triple quotes """ """ as the very first thing in a function, class, or file.

Think of it like the **instruction label on a medicine bottle**: it tells anyone using your code what it's for, without them reading all the code inside.

**Example: Docstring in a function**

```bash
def add(a, b):
    """Return the sum of two numbers."""
    return a + b
```
The text in triple quotes is the docstring. **It must be the first line inside the function**.

**Reading a docstring**: Python stores the docstring so you can view it later:

```bash
print(add.__doc__)
```
Output:
```bash
Return the sum of two numbers.
```
You can also use:
```bash
help(add)
```
| Docstring | Comment |
|---|---|
| Uses `""" """` | Uses `#` |
| Explains **what** code does | Explains **how/why** on a specific line |
| Can be read with `help()` | Ignored completely by Python |
| Goes at the start of a function/class/file | Can go anywhere |

## Decorators in Python
A decorator is a function that adds extra behavior to another function, without changing that function's code.

Think of it like gift wrapping: the gift (your function) stays the same, but the wrapping adds something extra around it.

**Example: simple function**
```bash
def say_hi():
    print("Hi")

greet = say_hi    # no brackets, so we're not calling it
greet()           # Hi
```
Next build a simple decorator

```bash
def my_decorator(func):
    def wrapper():
        print("Before the function")
        func()
        print("After the function")
    return wrapper
```
- `my_decorator` takes a function (`func`) as input
- `wrapper` is a new function that runs extra code, then calls `func`
- `my_decorator` returns `wrapper`

Using it with the @ symbol

```bash
@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```
Output
```
Before the function
Hello!
After the function
```
The @my_decorator line is just a shortcut for:
```bash
say_hello = my_decorator(say_hello)
```
A decorator is a function that takes another function, wraps extra behavior around it, and returns the new version. You apply it by writing @decorator_name above a function.

Why use decorators?
- **Reuse code**: write the extra behavior once, apply it to many functions
- **Keep functions clean**: logging, timing, and login checks stay out of your main logic
- Used a lot in frameworks like Flask and Django