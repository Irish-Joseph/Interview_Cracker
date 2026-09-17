"""
Topic: Comprehensions — building collections in one readable expression.

Concepts:
- List, dict and set comprehensions
- Filtering with a trailing `if`, transforming with a leading expression
- Conditional expressions inside a comprehension (`a if cond else b`)
- Nested loops vs nested comprehensions
- Generator expressions: the lazy, memory-cheap sibling
- When a plain for-loop is still the better choice

A comprehension replaces the "create empty list -> loop -> append" ritual.
Read it right-to-left: source first, filter next, transform last.

Time Complexity: O(n) — one pass over the source, same as the loop it replaces
Space Complexity: O(n) for list/dict/set comprehensions, O(1) for generators
"""

# --- The pattern it replaces ---------------------------------------------

temperatures_c = [0, 12, 21, 30, 37]

# The long way:
loop_result = []
for c in temperatures_c:
    loop_result.append(c * 9 / 5 + 32)

# The comprehension way — same result, one expression:
comp_result = [c * 9 / 5 + 32 for c in temperatures_c]

print("loop:       ", loop_result)
print("comprehension:", comp_result)
print("identical:  ", loop_result == comp_result)

# --- Filtering: the trailing `if` -----------------------------------------

numbers = range(1, 21)

evens = [n for n in numbers if n % 2 == 0]
divisible_by_3_and_5 = [n for n in numbers if n % 3 == 0 if n % 5 == 0]

print()
print("evens:            ", evens)
print("multiples of 15:  ", divisible_by_3_and_5)

# --- Transforming conditionally: the *leading* if/else --------------------

# Note the position. A trailing `if` DROPS items; a leading `if/else`
# CHANGES them but keeps every item.
labels = ["even" if n % 2 == 0 else "odd" for n in range(1, 7)]
print("labels (nothing dropped):", labels)

# --- Dict comprehensions --------------------------------------------------

products = [("laptop", 1200), ("mouse", 25), ("monitor", 300), ("cable", 8)]

price_by_name = {name: price for name, price in products}
affordable = {name: price for name, price in products if price < 100}
inverted = {price: name for name, price in products}

print()
print("price_by_name:", price_by_name)
print("under $100:   ", affordable)
print("inverted:     ", inverted)

# A very common use: reshape a dict, keeping the keys.
with_tax = {name: round(price * 1.2, 2) for name, price in price_by_name.items()}
print("with 20% tax: ", with_tax)

# --- Set comprehensions: transform and dedupe in one step -----------------

words = ["Python", "rust", "PYTHON", "Go", "go", "rust"]
normalized = {w.lower() for w in words}
print()
print("unique lowercase words:", sorted(normalized))

# --- Nested loops ---------------------------------------------------------

# Two `for` clauses read in the same order as nested for-loops:
#   for suit in suits:
#       for rank in ranks:
suits = ["S", "H"]  # spades, hearts
ranks = ["A", "K", "Q"]
deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
print()
print("deck:", deck)

# --- Flattening vs nesting ------------------------------------------------

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

flat = [value for row in matrix for value in row]          # one flat list
transposed = [[row[i] for row in matrix] for i in range(3)]  # list of lists

print("flat:      ", flat)
print("transposed:", transposed)

# --- Generator expressions: same syntax, parentheses, lazy ----------------

# A list comprehension builds every item up front. A generator expression
# produces items on demand, so it never holds the whole sequence in memory.
squares_list = [n * n for n in range(1_000_000)]      # ~40 MB of ints
squares_gen = (n * n for n in range(1_000_000))       # a few hundred bytes

print()
print("list object:     ", type(squares_list).__name__, "- length", len(squares_list))
print("generator object:", type(squares_gen).__name__, "- consumed lazily")

# Perfect for feeding an aggregate function that only needs one item at a time:
total = sum(n * n for n in range(1_000_000))
any_negative = any(n < 0 for n in flat)
print("sum of squares:  ", total)
print("any negative:    ", any_negative)

# --- When NOT to use a comprehension --------------------------------------

# Comprehensions are for *building a collection*. If you only need side
# effects, or the logic needs try/except or several statements, use a loop.
#
#   BAD:  [print(x) for x in items]        # builds a throwaway list of None
#   GOOD: for x in items: print(x)
#
# And once a comprehension needs a second line to stay readable, a plain
# loop is usually clearer than squeezing it in.

readable_enough = [
    name.title()
    for name, price in products
    if price > 20
]
print()
print("split across lines is fine:", readable_enough)
