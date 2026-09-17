"""
Topic: Find the missing number in a sequence.

Concepts:
- The mathematical sum formula for 1..n (Gauss's formula)
- Set lookup for uniqueness checking

Given a list that should contain every integer from 1 to n
with exactly one number missing, find the missing value.

Example:
Input:  [1, 2, 4, 5, 6]   (n = 6)
Expected sum: 6 * 7 // 2 = 21
Actual sum:   18
Output: 3

Time Complexity: O(n)
Space Complexity: O(1)
"""


def find_missing(numbers):
    n = len(numbers) + 1          # the sequence should be 1..n
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(numbers)
    return expected_sum - actual_sum


# --- Demo with several cases -------------------------------------------

cases = [
    [1, 2, 4, 5, 6],      # missing 3
    [1, 2, 3, 4],         # missing 5
    [2, 3, 4],            # missing 1
]

for case in cases:
    print(f"numbers={case!r:24} missing={find_missing(case)}")

# --- A variation: find ALL missing numbers in a range using a set -------
#
# When more than one number can be missing, the sum trick no longer works.
# Instead, load the numbers into a set (O(1) lookups) and scan the range.


def missing_in_range(numbers, start, end):
    present = set(numbers)                      # O(1) membership tests
    return [x for x in range(start, end + 1) if x not in present]


print(f"missing in 1..8: {missing_in_range([2, 4, 8], 1, 8)}")
# -> [1, 3, 5, 6, 7]
