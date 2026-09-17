# Python Interview Questions

---

### 🟢 Q. Mutable vs immutable — and why does it matter?

**Answer.** Immutable: `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`.
Mutable: `list`, `dict`, `set`, `bytearray`, most custom classes.

It decides three things: whether a value can be a dict key (hashable, which
requires immutable), whether passing it to a function can change the caller's
object, and whether it is safe to share between threads.

The classic bug it causes:

```python
def append_to(item, target=[]):      # DANGER: evaluated once, at def time
    target.append(item)
    return target

append_to(1)   # [1]
append_to(2)   # [1, 2]  <- the same list, still there
```

Default arguments are evaluated **once**, when the function is defined. Use
`None` as the sentinel:

```python
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

---

### 🟢 Q. `is` vs `==`?

**Answer.** `==` compares **values** (via `__eq__`); `is` compares **identity** —
whether both names point to the same object.

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b    # True  — same contents
a is b    # False — two distinct objects
```

Use `is` only for singletons: `is None`, `is True`, `is False`.

The confusing part is small-integer and string caching. `256 is 256` is True
because CPython interns small integers (−5 to 256); `1000 is 1000` may be False
depending on context. This is an implementation detail you must never rely on —
and a favourite trick question.

---

### 🔴 Q. What is the GIL and what does it mean for you?

**Answer.** The Global Interpreter Lock is a mutex ensuring only one thread
executes Python bytecode at a time, even on a many-core machine. It exists
because CPython's reference-counting memory management is not thread-safe, and
one coarse lock was far simpler and faster for single-threaded code than locking
every object.

The practical consequence:

- **CPU-bound work gets no speedup from threads.** Four threads on four cores
  still execute one at a time. Use `multiprocessing` (separate interpreters,
  separate GILs) or a native extension.
- **I/O-bound work does benefit**, because the GIL is released around blocking
  I/O. Threads and `asyncio` both work well here.

Worth knowing this is changing: PEP 703 adds an optional free-threaded build
(3.13+) with no GIL, and 3.12+ supports per-interpreter GILs. Saying "the GIL is
being removed as an *option*, gradually" is more accurate than either "it's gone"
or "Python can't do parallelism".

---

### 🟡 Q. What is a generator and why use one?

**Answer.** A function containing `yield`. Calling it returns a lazy iterator
that computes values on demand rather than building a list.

```python
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()       # one line in memory, not the whole file
```

Two benefits: **constant memory** regardless of input size, and the ability to
represent infinite sequences. The costs: you can only iterate once, and you
cannot index or take `len()`.

Use `()` instead of `[]` to get a generator expression:
`sum(x*x for x in range(10**8))` never allocates the list. Worked example:
[`examples/python/generators/log_pipeline_with_generators.py`](../../examples/python/generators/log_pipeline_with_generators.py).

---

### 🟡 Q. What is a decorator?

**Answer.** A callable that takes a function and returns a replacement, used to
add behaviour without editing the original.

```python
import functools, time

def timed(func):
    @functools.wraps(func)            # preserve __name__, __doc__, signature
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
    return wrapper

@timed
def work(): ...
```

`@timed` is exactly `work = timed(work)`.

**`functools.wraps` is the detail interviewers check for.** Without it the
decorated function reports the wrapper's name and loses its docstring, which
breaks introspection, documentation tools and debugging. Worked example:
[`examples/python/decorators/retry_decorator_with_backoff.py`](../../examples/python/decorators/retry_decorator_with_backoff.py).

---

### 🟡 Q. Shallow vs deep copy?

**Answer.** A **shallow** copy (`list(x)`, `x[:]`, `copy.copy`) makes a new outer
object holding **references to the same inner objects**. A **deep** copy
(`copy.deepcopy`) recursively copies everything.

```python
import copy
original = [[1, 2], [3, 4]]
shallow = copy.copy(original)
shallow[0].append(99)
original          # [[1, 2, 99], [3, 4]]  <- mutated!

deep = copy.deepcopy(original)
deep[0].append(100)
original          # unchanged
```

Deep copy is slower and fails or loops on some structures — it handles cycles,
but not open file handles or sockets. Prefer immutable data over copying.

---

### 🟡 Q. What does a context manager do?

**Answer.** Guarantees cleanup via `__enter__` / `__exit__`, so a resource is
released even if an exception is raised.

```python
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:                          # runs on exception too
        print(f"{label}: {time.perf_counter() - start:.3f}s")
```

`with open(...)` is the everyday example: the file closes on any exit path.
Worked example:
[`examples/python/context-managers/custom_context_managers.py`](../../examples/python/context-managers/custom_context_managers.py).

---

### 🟡 Q. `__str__` vs `__repr__`?

**Answer.** `__repr__` is for **developers** — unambiguous, ideally valid Python
that would recreate the object. It is what the REPL and containers show.
`__str__` is for **users** — readable.

If you implement only one, implement `__repr__`: `__str__` falls back to it, but
not the other way round. Worked example:
[`examples/python/oop/dunder_methods.py`](../../examples/python/oop/dunder_methods.py).

---

### 🟡 Q. What are `*args` and `**kwargs`?

**Answer.** `*args` collects extra positional arguments into a tuple; `**kwargs`
collects extra keyword arguments into a dict. In a *call*, the same symbols
unpack:

```python
def f(a, b, c): ...
values = [1, 2, 3]
f(*values)                      # unpacks positionally

config = {"a": 1, "b": 2, "c": 3}
f(**config)                     # unpacks by keyword
```

This is what lets a decorator wrap any function signature.
