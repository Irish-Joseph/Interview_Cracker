"""
Topic: Mutable default arguments and the sentinel pattern.

Concepts:
- Defaults are evaluated once, when the function is defined
- Why a list default leaks state between calls
- Using None or a private sentinel for per-call values

Run: python examples/python/functions/mutable_default_arguments.py
Expected output is asserted by the program.
"""


def append_bad(value: int, bucket: list[int] = []) -> list[int]:
    """The same list is reused on every call that omits bucket."""
    bucket.append(value)
    return bucket


def append_safe(value: int, bucket: list[int] | None = None) -> list[int]:
    """Create a fresh list only when the caller omitted one."""
    if bucket is None:
        bucket = []
    bucket.append(value)
    return bucket


_MISSING = object()


def configure(timeout: int | None | object = _MISSING) -> str:
    """A sentinel distinguishes omitted from explicitly passed None."""
    if timeout is _MISSING:
        return "use inherited timeout"
    if timeout is None:
        return "disable timeout"
    return f"timeout={timeout}"


first = append_bad(1)
second = append_bad(2)
assert first is second
assert second == [1, 2]

safe_first = append_safe(1)
safe_second = append_safe(2)
assert safe_first is not safe_second
assert safe_first == [1] and safe_second == [2]

explicit: list[int] = []
assert append_safe(3, explicit) is explicit

assert configure() == "use inherited timeout"
assert configure(None) == "disable timeout"
assert configure(30) == "timeout=30"

print("bad calls share:", second)
print("safe calls:", safe_first, safe_second)
print(configure(), "/", configure(None), "/", configure(30))
