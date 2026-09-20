"""
Challenge:  Remove Duplicates from Sorted Array
Pattern:    Two pointers (read and write)
Difficulty: Easy

PROBLEM
-------
Given an array sorted in non-decreasing order, remove the duplicates
*in place* such that each element appears only once. Return the length of
the array after removal.

The first `k` positions of the input array must hold the deduplicated
values (in their original order). You may overwrite the rest; no extra
array may be used.

EXAMPLES
--------
[1, 1, 2]                 -> 2   (array now starts [1, 2, _])
[0, 0, 1, 1, 1, 2, 3, 4] -> 5
[]                       -> 0
[7]                      -> 1

CONSTRAINTS
-----------
- The input is sorted (that is what makes O(1)-space dedup possible).
- Modify the input in place; O(1) extra space.
- Only the first k positions matter for the result.

HINT
----
Use two pointers that both move forward: `read` scans the array, and
`write` marks where the next *new* value goes. You only advance `write`
when the value at `read` differs from the value currently at `write`.
The return value is not len(arr) — think about what `write` ends up equal to.

COMPLEXITY
----------
Time:  O(n) - single pass
Space: O(1) - in place
"""


def remove_duplicates(arr: list[int]) -> int:
    if not arr:
        return 0

    write = 1  # index where the next unique value will be stored
    for read in range(1, len(arr)):
        if arr[read] != arr[write - 1]:
            arr[write] = arr[read]
            write += 1
    return write  # `write` is one past the last kept element


def _tests() -> None:
    # Empty input.
    assert remove_duplicates([]) == 0

    # Single element.
    a = [7]
    assert remove_duplicates(a) == 1
    assert a == [7]

    # Classic cases.
    a = [1, 1, 2]
    assert remove_duplicates(a) == 2
    assert a[:2] == [1, 2]

    a = [0, 0, 1, 1, 1, 2, 3, 4]
    assert remove_duplicates(a) == 5
    assert a[:5] == [0, 1, 2, 3, 4]

    # All equal: the naive "compare to previous input element" approach
    # works here, but the important property is that positions after k
    # may hold anything.
    a = [5, 5, 5, 5]
    assert remove_duplicates(a) == 1
    assert a[:1] == [5]

    # No duplicates: length unchanged.
    a = [1, 2, 3]
    assert remove_duplicates(a) == 3
    assert a == [1, 2, 3]

    # Negatives and interleaved values.
    a = [-3, -3, -1, -1, 0]
    assert remove_duplicates(a) == 3
    assert a[:3] == [-3, -1, 0]

    # Cross-check against a brute-force reference on randomised inputs.
    import random

    random.seed(2026)
    for _ in range(300):
        n = random.randint(0, 40)
        original = sorted(random.randint(-10, 10) for _ in range(n))
        working = list(original)
        k = remove_duplicates(working)
        reference = list(dict.fromkeys(original))  # unique, order kept
        assert working[:k] == reference, (original, working, k)
        assert k == len(reference)

    print("remove_duplicates: all tests passed")


if __name__ == "__main__":
    _tests()
