"""
Shallow copy vs deep copy (and why assignment is neither)

Concepts:
  - `a = b` shares the object; only the name is new
  - `copy.copy` copies the *container*, not its contents
  - `copy.deepcopy` copies the whole graph, including cycles
  - The rule of thumb: shallow is safe only when the contents are immutable

Run: python examples/python/basics/shallow_vs_deep_copy.py
Expected output: at the bottom of this file.
"""

import copy

# --- 1. Assignment: two names, one object -------------------------------

original = [[1, 2], [3, 4]]
alias = original            # no copy at all

alias[0][0] = 99
print("after mutating 'alias', original is:", original)
# The mutation is visible through the alias. This is the bug that the
# other three lines below exist to prevent.

# --- 2. Shallow copy: new container, shared contents ---------------------

original = [[1, 2], [3, 4]]
shallow = copy.copy(original)

print("shallow is a different list?  ", shallow is not original)
print("but the rows are shared?      ", shallow[0] is original[0])

shallow.append([5])          # fine: only the outer list is touched
original.append([6])         # fine: the other way around
print("after independent appends:")
print("  original:", original)
print("  shallow: ", shallow)

shallow[0][0] = 99           # crosses the shared row
print("after shallow[0][0] = 99, original[0] is:", original[0])

# Shallow copy is SAFE when contents are immutable, which is why a
# tuple-of-ints or a dict of scalars survives `copy.copy` just fine:
point = copy.copy((3, 4))
point2 = copy.copy({"x": 1, "y": 2})
print("immutable contents, shallow is enough:", point, point2)

# --- 3. Deep copy: the whole graph ----------------------------------------

original = {"a": [1, 2], "b": {"c": [3, 4]}}
deep = copy.deepcopy(original)

deep["a"][0] = 99
deep["b"]["c"][1] = 98
print("after deep mutations, original is unchanged:", original)

# --- 4. deepcopy handles reference cycles ---------------------------------

node = {"name": "root", "child": None}
node["child"] = node        # a cycle: root -> itself

dup = copy.deepcopy(node)
print("cycle copied? dup is node:", dup is node,
      "| dup's child is dup:", dup["child"] is dup,
      "| inner link preserved:", node["child"] is node)

# copy.copy on the same dict would also work (it shares the cycle),
# but deepcopy is what you reach for when you cannot trust the graph.

# --- 5. The cost asymmetry -------------------------------------------------

# Shallow copy of a list of N references: O(N), and that is the whole cost.
# Deep copy re-creates every nested object: O(size of the graph).
# So the discipline is: use `copy.copy` (or list(x) / dict(x)) by default,
# and pay for deepcopy only when contents are mutable AND must be private.

# --- Actual output ---------------------------------------------------------
# after mutating 'alias', original is: [[99, 2], [3, 4]]
# shallow is a different list?   True
# but the rows are shared?       True
# after independent appends:
#   original: [[1, 2], [3, 4], [6]]
#   shallow:  [[1, 2], [3, 4], [5]]
# after shallow[0][0] = 99, original[0] is: [99, 2]
# immutable contents, shallow is enough: (3, 4) {'x': 1, 'y': 2}
# after deep mutations, original is unchanged: {'a': [1, 2], 'b': {'c': [3, 4]}}
# cycle copied? dup is node: False | dup's child is dup: True | inner link preserved: True
