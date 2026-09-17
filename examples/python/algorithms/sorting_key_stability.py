"""
Topic: Sorting in Python — key functions, stability, multi-key and
       the decorate-sort-undecorate pattern.

Concepts:
- The key= parameter: sort by a derived value, compare the original
- Stability: equal keys keep their INPUT order (guaranteed in Python)
- Multi-key sorting: tuple keys, reverse per-field with negation
- reverse=True vs sorted(..., reverse=True) on the key
- The DsuD pattern for "sort by expensive-to-compute property"
- operator.itemgetter / attrgetter as fast key functions

Time Complexity: Timsort — O(n log n) worst case, O(n) on nearly-sorted
"""

import operator
from typing import NamedTuple


# --- 1. key=: sort by a derived value -------------------------------------

words = ["banana", "pie", "Washington", "book"]

by_length = sorted(words, key=len)
print("by length:      ", by_length)
# -> ['pie', 'book', 'banana', 'Washington']

by_upper = sorted(words, key=str.upper)
print("case-insensitive:", by_upper)
# -> ['banana', 'book', 'pie', 'Washington']


# --- 2. Stability: ties keep their original order ----------------------------

# (word, arrival_order) — sort by length; equal lengths preserve arrival.
items = [("fig", 1), ("pie", 2), ("cat", 3), ("dog", 4)]
stable = sorted(items, key=lambda t: len(t[0]))
print("stable by len:  ", [w for w, _ in stable])
# -> ['fig', 'pie', 'cat', 'dog']  (ties keep arrival order 1,2,3,4)

# Prove it: reverse the INPUT order, same result shape flips.
stable_rev_input = sorted(list(reversed(items)), key=lambda t: len(t[0]))
print("stable reversed:", [w for w, _ in stable_rev_input])
# -> ['dog', 'cat', 'pie', 'fig']  (now arrival order 4,3,2,1)


# --- 3. Multi-key sorting: tuple keys ------------------------------------------

class Employee(NamedTuple):
    name: str
    dept: str
    salary: int


team = [
    Employee("Eve", "eng", 90_000),
    Employee("Bob", "sales", 60_000),
    Employee("Al", "eng", 90_000),
    Employee("Cy", "sales", 70_000),
    Employee("Bo", "eng", 80_000),
]

# Primary: salary DESC, tie-break: name ASC.
# Trick: negate numeric fields to reverse just that field.
ranked = sorted(team, key=lambda e: (-e.salary, e.name))
print("ranked:         ", [(e.name, e.salary) for e in ranked])
# -> [('Al', 90000), ('Eve', 90000), ('Bo', 80000),
#     ('Cy', 70000), ('Bob', 60000)]

# Note: reverse=True would reverse ALL fields — you can't negate
# strings, so tuple-of-keys is the right tool for mixed directions.


# --- 4. itemgetter / attrgetter: fast, readable key functions --------------------

by_dept_then_salary = sorted(team, key=operator.attrgetter("dept", "salary"))
print("dept,salary:    ", [(e.dept, e.salary) for e in by_dept_then_salary])
# -> [('eng', 80000), ('eng', 90000), ('eng', 90000),
#     ('sales', 60000), ('sales', 70000)]

# itemgetter works the same way for tuples/lists:
pairs = [(1, "b"), (2, "a"), (1, "a")]
print("itemgetter:     ", sorted(pairs, key=operator.itemgetter(1, 0)))
# -> [(1, 'a'), (2, 'a'), (1, 'b')]


# --- 5. DsuD: decorate-sort-undecorate ---------------------------------------------
# When the sort key is EXPENSIVE to compute, compute it once per element.
# (Modern Python's key= already does this internally, but the pattern
#  matters when the key needs shared state or memoization.)

def expensive_score(text: str) -> float:
    """Pretend this is costly (e.g. an API call or heavy computation)."""
    return sum(ord(c) for c in text) / len(text)


_cache: dict[str, float] = {}

def memoized_score(text: str) -> float:
    if text not in _cache:
        _cache[text] = expensive_score(text)
    return _cache[text]

log_lines = ["error db timeout", "info ok", "warn slow query", "error db down"]

# DsuD: build (key, index, value) triples, sort, unwrap.
decorated = [(memoized_score(line), i, line) for i, line in enumerate(log_lines)]
decorated.sort()
ordered = [line for _, _, line in decorated]
print("DsuD order:     ")
for line in ordered:
    print(f"   {line}")
# (ascending average char code; the index in the triple preserves
#  stability for equal scores)

# Compute cost: each distinct line scored exactly ONCE.
print(f"score cache size: {len(_cache)} (computed once per line)")

# --- 6. Practical: top-N without sorting everything ------------------------------------
# For "largest k of n", heapq.nlargest is O(n log k) — better than a
# full O(n log n) sort when k << n.
import heapq

values = list(range(1_000_000, 0, -1))  # descending 1M..1
top5 = heapq.nlargest(5, values)
print("top 5 of 1M:    ", top5)
# -> [1000000, 999999, 999998, 999997, 999996]

# Cheat sheet:
#   sorted(seq, key=f)       -> new list, sorted by f(x)
#   seq.sort(key=f)          -> in place
#   key=lambda x: (-num, str)-> multi-key, mixed directions
#   Timsort is STABLE        -> equal keys keep input order
#   heapq.nlargest(k, seq)   -> top-k without full sort
