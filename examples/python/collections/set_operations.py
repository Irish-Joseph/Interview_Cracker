"""
Topic: Set operations — the math toolkit for collections.

Concepts:
- Sets store unique, unordered items
- Union |, intersection &, difference -, symmetric difference ^
- Subsets / supersets (<=, >=)
- Frozen sets (hashable, usable as dict keys)
- Why sets are the right tool for membership tests and dedupe

Real-world uses: who's in both groups? which users are new?
which permissions overlap? Sets make these one-liners instead
of nested loops.

Time Complexity: O(min(len(a), len(b))) for the set operations below
Space Complexity: O(1) extra for the result set
"""


def show(label: str, result: set) -> None:
    print(f"{label:28} {sorted(result)}")


# --- Setup: two friend groups --------------------------------------------

alice_friends = {"Bob", "Carol", "Dan", "Eve"}
bob_friends = {"Carol", "Dan", "Frank", "Grace"}

# --- The core operations ---------------------------------------------------

show("union (either)", alice_friends | bob_friends)
show("intersection (both)", alice_friends & bob_friends)
show("difference (only alice)", alice_friends - bob_friends)
show("sym diff (either, not both)", alice_friends ^ bob_friends)

# Membership testing is O(1) on sets (O(n) on lists):
print()
print("'Eve' in alice's friends:", "Eve" in alice_friends)   # True
print("'Frank' in alice's friends:", "Frank" in alice_friends)  # False

# --- Deduplication: the most common set use case -----------------------------

tags = ["python", "rust", "python", "go", "rust", "go", "python"]
unique_tags = set(tags)
show("deduplicated tags", unique_tags)

# --- Subset checks -------------------------------------------------------------

core_team = {"Carol", "Dan"}
print()
print("core is subset of both:",
      core_team <= alice_friends and core_team <= bob_friends)  # True

# --- Frozen sets: hashable, so they can be dict keys ---------------------------

# A regular set can't be a dict key (unhashable). frozenset can:
cache = {
    frozenset({"coffee", "milk"}): 3.50,   # latte
    frozenset({"coffee"}): 2.00,           # espresso
}

order = frozenset({"milk", "coffee"})      # same set, any order
print(f"price for {sorted(order)}: ${cache[order]:.2f}")  # $3.50

# --- Performance note: sets vs lists for membership -----------------------------

import timeit

big_set = set(range(1_000_000))
big_list = list(range(1_000_000))

t_set = timeit.timeit(lambda: 999_999 in big_set, number=100_000)
t_list = timeit.timeit(lambda: 999_999 in big_list, number=100)
print()
print(f"membership in set of 1M   (100k checks): {t_set:.3f}s")
print(f"membership in list of 1M  (100 checks):  {t_list:.3f}s")
# The list version is ~1000x slower per check — that's O(1) vs O(n).
