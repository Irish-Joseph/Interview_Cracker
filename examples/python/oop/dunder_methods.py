"""
Topic: Dunder methods — making your class behave like a built-in type.

Concepts:
- __repr__ vs __str__ (developer view vs user view)
- __eq__ and __hash__ (and why they travel together)
- __lt__ plus @total_ordering for sorting and comparison
- __len__, __bool__, __contains__, __iter__, __getitem__
- __add__ / __mul__ for operator overloading, and NotImplemented
- __call__ to make an instance behave like a function

Python's operators are not special syntax reserved for built-in types.
`a + b` is `type(a).__add__(a, b)`; `len(x)` is `type(x).__len__(x)`.
Implement the method and your own class joins in.

Example:
    Money(5, "EUR") + Money(2.50, "EUR")  ->  Money(7.5, 'EUR')
"""

from functools import total_ordering


# --- 1. Representation: __repr__ and __str__ ------------------------------


class Money:
    """An amount in a single currency. Immutable by convention."""

    __slots__ = ("amount", "currency")

    def __init__(self, amount: float, currency: str = "EUR"):
        self.amount = round(float(amount), 2)
        self.currency = currency

    # __repr__ is for developers: unambiguous, ideally valid Python.
    # It is what the REPL, containers and debuggers show.
    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    # __str__ is for users: readable. Without it, str() falls back to __repr__.
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    # --- 2. Equality and hashing ------------------------------------------

    # Without __eq__, two distinct Money objects are never equal, because the
    # default compares identity: "is this the same object?"
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented  # let the other type try; then falls back to False
        return (self.amount, self.currency) == (other.amount, other.currency)

    # Defining __eq__ sets __hash__ to None, making the class unhashable.
    # Restore it, and keep it consistent: equal objects MUST hash equal or
    # sets and dicts will misbehave.
    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    # --- 3. Arithmetic -----------------------------------------------------

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: float) -> "Money":
        if not isinstance(factor, (int, float)):
            return NotImplemented
        return Money(self.amount * factor, self.currency)

    # __rmul__ handles the reversed operand order: 3 * money.
    # int.__mul__(3, money) returns NotImplemented, so Python tries this.
    __rmul__ = __mul__

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    # --- 4. Truthiness -----------------------------------------------------

    # Without __bool__ every instance is truthy. Here zero means "nothing".
    def __bool__(self) -> bool:
        return self.amount != 0


usd = Money(19.99, "USD")
print("1. repr:", repr(usd))
print("1. str: ", str(usd))
print("1. inside a list (uses repr):", [usd])

print()
print("2. equal by value:", Money(5, "EUR") == Money(5, "EUR"))
print("2. wrong currency:", Money(5, "EUR") == Money(5, "USD"))
print("2. against an int:", Money(5, "EUR") == 5)
print("2. usable in a set:", {Money(5, "EUR"), Money(5, "EUR"), Money(1, "EUR")})

print()
print("3. add:     ", Money(5, "EUR") + Money(2.50, "EUR"))
print("3. multiply:", Money(5, "EUR") * 3)
print("3. reversed:", 3 * Money(5, "EUR"))
print("3. negate:  ", -Money(5, "EUR"))
try:
    Money(5, "EUR") + Money(5, "USD")
except ValueError as err:
    print("3. mixed currencies ->", err)

print()
print("4. bool(zero):", bool(Money(0, "EUR")), "| bool(5 EUR):", bool(Money(5, "EUR")))


# --- 5. Ordering: one method plus a decorator -----------------------------


@total_ordering  # derives <=, >, >= from __eq__ and __lt__
class Version:
    """A semantic version that sorts correctly (1.10.0 > 1.9.0)."""

    def __init__(self, text: str):
        self.text = text
        self.parts = tuple(int(p) for p in text.split("."))

    def __repr__(self) -> str:
        return f"Version({self.text!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other: "Version") -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts  # tuples compare element by element

    def __hash__(self) -> int:
        return hash(self.parts)


versions = [Version("1.9.0"), Version("1.10.0"), Version("0.4.12"), Version("1.9.3")]
print()
print("5. sorted:", sorted(versions))   # sorting needs only __lt__
print("5. max:   ", max(versions))
print("5. 1.10.0 > 1.9.0:", Version("1.10.0") > Version("1.9.0"))  # via total_ordering


# --- 6. Container protocol ------------------------------------------------


class Playlist:
    """A container: len(), `in`, iteration, indexing and slicing."""

    def __init__(self, name: str, tracks: list[str] | None = None):
        self.name = name
        self._tracks = list(tracks or [])

    def __repr__(self) -> str:
        return f"Playlist({self.name!r}, {self._tracks!r})"

    def __len__(self) -> int:
        return len(self._tracks)

    def __contains__(self, track: object) -> bool:
        # Without this, `in` falls back to iteration: correct, but O(n) either
        # way here — on a set-backed container it would be the difference.
        return track in self._tracks

    def __iter__(self):
        return iter(self._tracks)

    def __getitem__(self, index):
        # Handling slices costs one line and makes the class feel native.
        if isinstance(index, slice):
            return Playlist(f"{self.name}[slice]", self._tracks[index])
        return self._tracks[index]

    def __setitem__(self, index: int, value: str) -> None:
        self._tracks[index] = value


playlist = Playlist("focus", ["ambient", "piano", "rain", "lofi"])
print()
print("6. len:         ", len(playlist))
print("6. contains:    ", "rain" in playlist, "|", "metal" in playlist)
print("6. index:       ", playlist[0], "| negative:", playlist[-1])
print("6. slice:       ", playlist[1:3])
print("6. iteration:   ", [t.upper() for t in playlist])
playlist[0] = "drone"
print("6. after setitem:", playlist)


# --- 7. __call__: an instance that behaves like a function -----------------


class Accumulator:
    """Callable object: like a closure, but with inspectable state."""

    def __init__(self, start: float = 0):
        self.total = start
        self.calls = 0

    def __call__(self, value: float) -> float:
        self.calls += 1
        self.total += value
        return self.total

    def __repr__(self) -> str:
        return f"Accumulator(total={self.total}, calls={self.calls})"


running = Accumulator()
print()
print("7. call results:", [running(n) for n in (10, 5, 2.5)])
print("7. state kept:  ", running)
print("7. callable():  ", callable(running))

# --- Takeaways -------------------------------------------------------------
#
# - Always write __repr__; it pays for itself the first time you debug.
# - __eq__ without __hash__ makes a class unusable in sets and as dict keys.
# - Return NotImplemented (not False, not an exception) for operand types you
#   do not support, so Python can try the other operand's reflected method.
# - Implement only the protocols that genuinely fit the type. `dataclasses`
#   can generate __init__, __repr__, __eq__ and ordering for you.
