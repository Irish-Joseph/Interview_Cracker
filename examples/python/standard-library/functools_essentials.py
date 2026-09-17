"""
Topic: functools - caching, partial application and single dispatch.

The functools module turns several recurring chores into one-liners:

- cache / lru_cache : memoise a pure function, turning exponential work linear
- partial           : pre-fill some arguments and get a new callable back
- reduce            : fold a sequence into one value
- singledispatch    : pick an implementation based on the argument's type
- cached_property   : compute an attribute once, on first access

Concepts:
- Why memoisation needs the function to be PURE and its arguments hashable
- cache_info() for hit/miss telemetry, cache_clear() to reset
- partial vs a lambda, and why partial survives pickling
- singledispatch as an alternative to a long isinstance chain

Example output is printed at the bottom of the file.
"""

import functools
import time
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 1. cache / lru_cache - memoisation
# ---------------------------------------------------------------------------

calls_without_cache = 0


def fib_slow(n):
    """Naive recursion: O(2^n), because it recomputes the same values."""
    global calls_without_cache
    calls_without_cache += 1
    if n <= 1:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)


@functools.cache
def fib_fast(n):
    """Identical body; @cache makes each n computed exactly once -> O(n).

    functools.cache (3.9+) is lru_cache(maxsize=None): an unbounded dict
    keyed by the arguments. Use lru_cache(maxsize=...) when the key space is
    large and you need eviction.
    """
    if n <= 1:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)


@functools.lru_cache(maxsize=2)
def expensive_lookup(key):
    """maxsize=2 keeps only the two most recently used entries."""
    time.sleep(0.001)          # stand-in for real work
    return key.upper()


# The cache keys on the ARGUMENTS, so they must be hashable. A list argument
# raises TypeError; pass a tuple instead.
@functools.cache
def total(numbers):
    return sum(numbers)


# ---------------------------------------------------------------------------
# 2. partial - pre-fill arguments
# ---------------------------------------------------------------------------


def log(level, module, message):
    return f"[{level}] {module}: {message}"


# Each partial locks in the leading positional arguments.
warn = functools.partial(log, "WARN")
db_warn = functools.partial(warn, "database")

# Keyword arguments work too, and remain overridable.
to_base_2 = functools.partial(int, base=2)


# ---------------------------------------------------------------------------
# 3. reduce - fold a sequence to a single value
# ---------------------------------------------------------------------------


def product(numbers):
    """reduce applies the function pairwise, left to right.

    Prefer sum()/max()/math.prod() when they exist - they are clearer and
    faster. reduce earns its place for genuinely custom folds.
    """
    return functools.reduce(lambda a, b: a * b, numbers, 1)


def merge_settings(layers):
    """A custom fold that has no built-in: later layers win."""
    return functools.reduce(lambda acc, layer: {**acc, **layer}, layers, {})


# ---------------------------------------------------------------------------
# 4. singledispatch - dispatch on the first argument's type
# ---------------------------------------------------------------------------


@functools.singledispatch
def describe(value):
    """Fallback, used when no registered type matches."""
    return f"{type(value).__name__}: {value!r}"


@describe.register
def _(value: int):
    return f"int {value} ({'even' if value % 2 == 0 else 'odd'})"


@describe.register
def _(value: str):
    return f"str of length {len(value)}"


@describe.register(list)
@describe.register(tuple)
def _(value):
    return f"sequence of {len(value)} item(s)"


# ---------------------------------------------------------------------------
# 5. cached_property - compute once per instance
# ---------------------------------------------------------------------------


@dataclass
class Report:
    rows: list
    _computed: list = field(default_factory=list)

    @functools.cached_property
    def summary(self):
        """Runs on first access; the result then replaces the attribute."""
        self._computed.append("summary")
        return {"count": len(self.rows), "total": sum(self.rows)}


if __name__ == "__main__":
    print("-- cache --")
    print("fib_slow(25) =", fib_slow(25), "in", calls_without_cache, "calls")
    print("fib_fast(25) =", fib_fast(25), "->", fib_fast.cache_info())
    fib_fast(25)          # already cached: one dict lookup, no recursion
    print("fib_fast(25) again ->", fib_fast.cache_info(), "(one more hit, no new misses)")

    print("-- lru_cache eviction (maxsize=2) --")
    for key in ["a", "b", "a", "c", "b"]:
        expensive_lookup(key)
    print(" ", expensive_lookup.cache_info())

    print("-- hashable arguments only --")
    print("  tuple works:", total((1, 2, 3)))
    try:
        total([1, 2, 3])
    except TypeError as error:
        print("  list fails:", error)

    print("-- partial --")
    print(" ", warn("auth", "token expiring"))
    print(" ", db_warn("connection pool exhausted"))
    print("  int('1011', base=2) ->", to_base_2("1011"))
    print("  partial keeps its pieces:", to_base_2.func.__name__, to_base_2.keywords)

    print("-- reduce --")
    print("  product([1,2,3,4]) =", product([1, 2, 3, 4]))
    print("  product([]) =", product([]), "(the initialiser makes this safe)")
    print("  merged:", merge_settings([
        {"host": "localhost", "port": 80},
        {"port": 8080},
        {"debug": True},
    ]))

    print("-- singledispatch --")
    for value in [42, 7, "hello", [1, 2, 3], (1, 2), 3.5]:
        print("  ", describe(value))

    print("-- cached_property --")
    report = Report(rows=[10, 20, 30])
    print("  first access: ", report.summary)
    print("  second access:", report.summary)
    print("  computed times:", len(report._computed), "(not 2)")

# Expected output:
# -- cache --
# fib_slow(25) = 75025 in 242785 calls
# fib_fast(25) = 75025 -> CacheInfo(hits=23, misses=26, maxsize=None, currsize=26)
# ...
# -- hashable arguments only --
#   tuple works: 6
#   list fails: unhashable type: 'list'
# -- partial --
#   [WARN] auth: token expiring
#   [WARN] database: connection pool exhausted
#   int('1011', base=2) -> 11
# -- singledispatch --
#    int 42 (even)
#    str of length 5
#    sequence of 3 item(s)
#    float: 3.5
