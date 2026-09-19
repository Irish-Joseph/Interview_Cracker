"""
Topic: Type hints - annotating code so tools can catch bugs before you run it.

Python stays dynamically typed at runtime: annotations are NOT enforced, and
passing the wrong type raises nothing by itself. Their value is that a type
checker (mypy, pyright) reads them and finds the mistake statically, and that
editors can then autocomplete and refactor reliably.

Concepts:
- Annotating parameters, returns, variables and class attributes
- Optional[X] / X | None, and why a None default needs it
- Collections: list[int], dict[str, int], tuple fixed vs variable length
- Sequence/Iterable/Mapping - accept the widest type you actually need
- Literal, TypedDict and NamedTuple for precise shapes
- Generics with TypeVar, and Protocol for structural typing
- get_type_hints() to read annotations at runtime, and `from __future__`

Nothing here requires a type checker to RUN, but running one is the point:
    pip install mypy && mypy examples/python/typing/type_hints_and_typing_module.py
"""

from __future__ import annotations  # annotations stay strings: cheaper, and
                                    # lets you reference names defined later

from dataclasses import dataclass
from typing import (
    Iterable,
    Literal,
    Mapping,
    NamedTuple,
    Protocol,
    Sequence,
    TypedDict,
    TypeVar,
    get_type_hints,
)

# ---------------------------------------------------------------------------
# 1. The basics
# ---------------------------------------------------------------------------


def greet(name: str, excited: bool = False) -> str:
    """Parameters and the return type. `-> None` for functions returning nothing."""
    return f"Hello {name}{'!' if excited else '.'}"


# A variable annotation. Useful when the value alone is ambiguous.
retries: int = 3
labels: list[str] = []


def find_user(user_id: int) -> str | None:
    """`str | None` (3.10+) is the modern spelling of Optional[str].

    A function that can return nothing MUST say so, or the checker will not
    warn callers who forget to handle the None.
    """
    users = {1: "ada", 2: "grace"}
    return users.get(user_id)


def truncate(text: str, limit: int | None = None) -> str:
    """A None default needs `| None` in the annotation, not just `int`."""
    if limit is None:
        return text
    return text[:limit]


# ---------------------------------------------------------------------------
# 2. Collections, and accepting the widest useful type
# ---------------------------------------------------------------------------


def total(numbers: Sequence[int]) -> int:
    """Sequence accepts list, tuple and range - anything indexable and sized.

    Annotating `list[int]` here would reject a tuple for no good reason. Rule
    of thumb: be permissive in what you ACCEPT, precise in what you RETURN.
    """
    return sum(numbers)


def count_words(words: Iterable[str]) -> dict[str, int]:
    """Iterable is wider still: it accepts a generator, which Sequence does not."""
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def lookup(config: Mapping[str, int], key: str, default: int = 0) -> int:
    """Mapping is the read-only view of a dict; use it when you never mutate."""
    return config.get(key, default)


# Fixed-length vs variable-length tuples mean different things:
Point = tuple[int, int]          # exactly two ints
Row = tuple[str, ...]            # any number of strings


def midpoint(a: Point, b: Point) -> Point:
    return ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)


# ---------------------------------------------------------------------------
# 3. Precise shapes: Literal, TypedDict, NamedTuple, dataclass
# ---------------------------------------------------------------------------

# Literal restricts a value to a fixed set, checked statically.
Format = Literal["csv", "json", "text"]


def render(rows: Sequence[Row], fmt: Format = "text") -> str:
    if fmt == "csv":
        return "\n".join(",".join(row) for row in rows)
    if fmt == "json":
        return "[" + ", ".join(str(list(row)) for row in rows) + "]"
    return "\n".join(" | ".join(row) for row in rows)


class UserRecord(TypedDict):
    """A dict with a KNOWN set of keys and per-key types.

    At runtime this is an ordinary dict - no validation happens. Its job is to
    let the checker catch a typo'd key or a wrong value type.
    """
    id: int
    name: str
    active: bool


class Coordinate(NamedTuple):
    """A tuple with named fields: immutable, unpackable, and typed."""
    lat: float
    lon: float

    def as_text(self) -> str:
        return f"{self.lat:.2f},{self.lon:.2f}"


@dataclass
class Job:
    """A mutable record. Annotations here are REQUIRED - dataclass reads them."""
    name: str
    attempts: int = 0
    tags: list[str] | None = None


# ---------------------------------------------------------------------------
# 4. Generics and Protocol
# ---------------------------------------------------------------------------

T = TypeVar("T")


def first(items: Sequence[T], default: T) -> T:
    """TypeVar ties the types together: pass a list[str] and you get a str back.

    Annotating `Sequence[object] -> object` would compile but lose that link,
    and the caller would have to cast.
    """
    return items[0] if items else default


class SupportsArea(Protocol):
    """Structural typing: anything with this method matches, no inheritance.

    This is the static-checking equivalent of duck typing.
    """

    def area(self) -> float: ...


class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side**2


def describe_area(shape: SupportsArea) -> str:
    # Square never mentions SupportsArea, yet it satisfies the protocol.
    return f"area = {shape.area():.1f}"


# ---------------------------------------------------------------------------
# 5. Annotations are not enforced at runtime
# ---------------------------------------------------------------------------


def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    print("-- basics --")
    print(" ", greet("Ada", excited=True))
    print("  find_user(1):", find_user(1), "| find_user(9):", find_user(9))
    print("  truncate:", truncate("abcdefgh", 3), "|", truncate("abcdefgh"))

    print("-- collections --")
    print("  total(list):", total([1, 2, 3]), "| total(tuple):", total((4, 5)))
    print("  total(range):", total(range(1, 5)))
    print("  count_words:", count_words(w for w in "a b a c a b".split()))
    print("  lookup:", lookup({"retries": 5}, "retries"), lookup({}, "retries", 1))
    print("  midpoint:", midpoint((0, 0), (10, 4)))

    print("-- precise shapes --")
    rows: list[Row] = [("ada", "36"), ("grace", "45")]
    print("  csv :", render(rows, "csv").replace("\n", " / "))
    print("  text:", render(rows).replace("\n", " / "))

    user: UserRecord = {"id": 1, "name": "ada", "active": True}
    print("  TypedDict is just a dict:", type(user).__name__, user)

    here = Coordinate(51.50, -0.12)
    lat, lon = here                       # still a tuple
    print("  NamedTuple:", here.as_text(), "| unpacked:", lat, lon)
    print("  dataclass:", Job("import", tags=["nightly"]))

    print("-- generics and protocol --")
    print("  first(['a','b'], 'z'):", first(["a", "b"], "z"))
    print("  first([], 0):", first([], 0))
    print("  protocol:", describe_area(Square(3)))

    print("-- not enforced at runtime --")
    # A checker flags this; Python runs it happily, because + is defined
    # for strings. THIS is why annotations alone are not validation.
    print("  add('a', 'b') =", add("a", "b"))   # type: ignore[arg-type]
    print("  add(1, 2)     =", add(1, 2))

    print("-- reading annotations at runtime --")
    print("  add:", get_type_hints(add))
    print("  Job fields:", {k: v.__name__ if hasattr(v, "__name__") else str(v)
                            for k, v in get_type_hints(Job).items()})

# Expected output:
#   -- basics --
#     Hello Ada!
#     find_user(1): ada | find_user(9): None
#   -- not enforced at runtime --
#     add('a', 'b') = ab          <- a type checker would reject this line
#     add(1, 2)     = 3
