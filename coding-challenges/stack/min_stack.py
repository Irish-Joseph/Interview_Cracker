"""
Challenge:  Min Stack
Pattern:    Stack (an auxiliary stack that mirrors the main one)
Difficulty: Medium

PROBLEM
-------
Design a stack that supports push, pop, top and retrieving the minimum
element — all in O(1) time.

class MinStack:
    def push(val)      # push val onto the stack
    def pop()          # remove the top element
    def top() -> int   # peek at the top
    def get_min() -> int  # the smallest element currently in the stack

EXAMPLES
--------
push(2); push(0); push(3)
get_min() -> 0
pop()                # removes 3
get_min() -> 0
pop()                # removes 0
get_min() -> 2       # the 0 left with it; 2 is the min again

CONSTRAINTS
-----------
- Up to 10^4 operations, values in [-10^5, 10^5].
- get_min() must be O(1): scanning the stack each time is O(n) and fails.
- A second stack is allowed; a second full *copy* of the data is not the
  point (though a mirror stack is the classic, clean answer).

HINT
----
Keep a second stack of the MINIMUM-so-far. On push, push min(val, current
min) onto it. On pop, pop both. The two stacks always stay the same
height, so the top of the min-stack is always the min of the current
stack — and the min is restored for free when the element that caused it
is popped.

COMPLEXITY
----------
Time:  O(1) per operation
Space: O(n) - the min mirror holds at most one entry per push
"""


class MinStack:
    def __init__(self) -> None:
        self._stack: list[int] = []
        self._mins: list[int] = []  # _mins[i] = min of _stack[:i+1]

    def push(self, value: int) -> None:
        self._stack.append(value)
        current_min = self._mins[-1] if self._mins else value
        self._mins.append(min(value, current_min))

    def pop(self) -> int:
        if not self._stack:
            raise IndexError("pop from empty MinStack")
        self._mins.pop()  # discard the min that belonged to this layer
        return self._stack.pop()

    def top(self) -> int:
        if not self._stack:
            raise IndexError("top of empty MinStack")
        return self._stack[-1]

    def get_min(self) -> int:
        if not self._mins:
            raise IndexError("min of empty MinStack")
        return self._mins[-1]


def _tests() -> None:
    # The specified example sequence.
    ms = MinStack()
    ms.push(2); ms.push(0); ms.push(3)
    assert ms.get_min() == 0
    ms.pop()
    assert ms.get_min() == 0
    ms.pop()
    assert ms.get_min() == 2

    # Duplicates of the minimum: popping one must not raise the min.
    ms = MinStack()
    ms.push(5); ms.push(1); ms.push(1)
    assert ms.get_min() == 1
    ms.pop()
    assert ms.get_min() == 1        # a 1 remains
    ms.pop()
    assert ms.get_min() == 5        # both 1s gone

    # top() is a peek, not a pop.
    ms = MinStack()
    ms.push(7)
    assert ms.top() == 7 and ms.top() == 7 and len(ms._stack) == 1

    # Pop from empty must fail, not return garbage.
    ms = MinStack()
    for method in (ms.pop, ms.top, ms.get_min):
        try:
            method()
        except IndexError:
            pass
        else:
            raise AssertionError(f"{method.__name__} on empty stack did not raise")

    # Randomised cross-check against a naive reference (full scan for min).
    import random

    random.seed(5)
    for trial in range(100):
        ms = MinStack()
        plain: list[int] = []
        for _ in range(200):
            op = random.random()
            if op < 0.45 or not plain:
                v = random.randint(-10, 10)
                ms.push(v)
                plain.append(v)
            elif op < 0.75:
                assert ms.pop() == plain.pop()
            else:
                assert ms.top() == plain[-1]
            if plain:  # only compare mins while the stack is non-empty
                assert ms.get_min() == min(plain), (trial, plain)

    print("min_stack: all tests passed")


if __name__ == "__main__":
    _tests()
