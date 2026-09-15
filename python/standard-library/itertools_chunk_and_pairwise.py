"""
Topic: Chunk sequences and get adjacent pairs with itertools.

Concepts:
- itertools.batched (Python 3.12+) and a manual chunking fallback
- The zip(*[iter(it)] * n) idiom for fixed-size chunks
- Pairwise iteration using zip of a sequence with itself shifted by one
- Working with iterators instead of materializing lists

Example:
Input:  numbers = [1, 2, 3, 4, 5, 6, 7]
Chunks of 3:  [1, 2, 3] [4, 5, 6] [7]
Pairs:        (1, 2) (2, 3) (3, 4) (4, 5) (5, 6) (6, 7)

Time Complexity: O(n) for both operations
"""

import sys
from itertools import islice


def chunked(iterable, size):
    """Yield successive fixed-size chunks from an iterable.

    Works on any iterable, including generators, and keeps a final
    partial chunk instead of dropping it.
    """
    it = iter(iterable)
    for first in it:
        # first anchors the chunk so an exhausted iterable still
        # yields its trailing partial chunk (e.g. [7] from 7 items of 3).
        yield [first, *islice(it, size - 1)]


def pairwise(iterable):
    """Yield adjacent (previous, current) pairs: (1,2) (2,3) (3,4) ..."""
    it = iter(iterable)
    previous, current = next(it, None), next(it, None)
    while current is not None:
        yield previous, current
        previous, current = current, next(it, None)


numbers = [1, 2, 3, 4, 5, 6, 7]

print("Chunks of 3:")
for chunk in chunked(numbers, 3):
    print(" ", chunk)

print("Adjacent pairs with their sums:")
for prev, cur in pairwise(numbers):
    print(f"  {prev} + {cur} = {prev + cur}")

# batched() exists in Python 3.12 and is the built-in chunking tool:
if sys.version_info >= (3, 12):
    from itertools import batched
    print("itertools.batched:", list(batched(numbers, 3)))
