"""
Topic: Custom context managers — the `with` statement under the hood.

Concepts:
- __enter__ / __exit__ protocol
- The class-based context manager
- @contextlib.contextmanager generator-based shortcut (yield)
- Exception flow: __exit__ sees (and can suppress) exceptions
- Cleanup that runs on EVERY path: normal exit and errors
- Nested context managers

`with` guarantees cleanup even when exceptions happen — the same
guarantee as try/finally, but with a cleaner shape.

Time/Space: n/a (resource-management pattern)
"""

import contextlib
import time
from typing import Iterator


# --- 1. Class-based context manager -----------------------------------------

class TimingContext:
    """Measures and reports how long a block runs.

    __enter__ runs BEFORE the block, __exit__ AFTER it —
    even if the block raises.
    """

    def __init__(self, label: str):
        self.label = label
        self.elapsed: float | None = None

    def __enter__(self) -> "TimingContext":
        # Return value becomes the `as` variable.
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.elapsed = time.perf_counter() - self._start
        status = "ok" if exc_type is None else f"raised {exc_type.__name__}"
        print(f"[{self.label}] {status} in {self.elapsed * 1000:.1f} ms")
        # Returning True would SUPPRESS the exception (swallow it).
        # Return False/None to let it propagate — the honest default.
        return False


with TimingContext("sleep") as t:
    time.sleep(0.02)
print("after: elapsed =", f"{t.elapsed * 1000:.1f} ms")

# Exception path: __exit__ STILL runs, and the error still propagates.
try:
    with TimingContext("boom"):
        raise ValueError("intentional")
except ValueError as e:
    print("propagated:", e)


# --- 2. Generator-based: @contextlib.contextmanager ---------------------------
#
# The `yield` is the boundary: code before it is __enter__,
# code after it is __exit__. The yielded value is the `as` target.
# If the body raises, the exception is re-raised at the yield
# point — so put cleanup BEFORE any code that must always run.

@contextlib.contextmanager
def working_directory_label(label: str) -> Iterator[str]:
    """A fake 'resource' that prints acquire/release around a block."""
    print(f"  acquiring {label}")
    try:
        yield label  # <- the with-block body runs HERE
    finally:
        # finally guarantees release even on exception.
        print(f"  releasing {label}")


with working_directory_label("db-connection") as resource:
    print(f"  using {resource}")

print()
try:
    with working_directory_label("lock") as resource:
        print(f"  holding {resource}")
        raise RuntimeError("crash while holding")
except RuntimeError as e:
    print("  propagated:", e)


# --- 3. Combining managers: ExitStack for dynamic counts -----------------------

@contextlib.contextmanager
def resource(name: str) -> Iterator[str]:
    print(f"  open  {name}")
    try:
        yield name
    finally:
        print(f"  close {name}")


# A fixed, known set: nested with.
with resource("a"), resource("b") as b:
    print(f"  both open, using {b}")
# closes in REVERSE order: b then a

print()

# A DYNAMIC set of resources: ExitStack manages them for you.
names = ["file1", "file2", "file3"]
with contextlib.ExitStack() as stack:
    handles = [stack.enter_context(resource(n)) for n in names]
    print(f"  {len(handles)} resources open: {handles}")
# ExitStack closes everything on exit, reverse order,
# even if the body (or a later acquisition) raises.

# Expected tail output:
#   open  file1
#   open  file2
#   open  file3
#   3 resources open: ['file1', 'file2', 'file3']
#   close file3
#   close file2
#   close file1
