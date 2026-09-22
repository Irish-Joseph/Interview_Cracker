"""
Challenge:  Alien Dictionary
Pattern:    Topological sort (Kahn's algorithm, indegrees)
Difficulty: Medium

PROBLEM
    Given a list of "words" written in some unknown alphabet whose
    lexicographic order produced that list, return the alphabet as a string
    (one letter per character) consistent with the observed order. Among
    several valid answers, return the lexicographically smallest. Return
    the empty string if the words are inconsistent with any total order.

EXAMPLES
    ["adc", "dfb", "cba", "cab"]     -> "badcf"  (b<a, a<d, d<c; f is unconstrained)
    ["ab", "ba"]                     -> "ab"  (one adjacent pair, one edge: a before b)
    ["ab", "ba", "aa"]               -> ""    (a < b AND b < a: a cycle)
    ["z"]                            -> "z"
    []                               -> ""

CONSTRAINTS
    - Lowercase letters only; each word is 1-30 characters.
    - Order information comes ONLY from the first pair of characters at
      which two adjacent words differ - "cab" < "cabz" tells you nothing.
    - One differing pair gives exactly one edge, repeated edges must not
      break the indegree count.

HINT
    Each differing adjacent pair is a constraint "x comes before y":
    build the graph, count indegrees, then repeatedly take the
    lexicographically smallest letter with indegree 0 (that choice is what
    makes the final answer the smallest valid one), peel its edges off,
    and continue. Fewer letters emitted than exist means a cycle.

COMPLEXITY
    Time: O(N + K) where N is the total number of characters (to read the
          word list) and K is the alphabet size (26) - the heap work is
          dominated by N for realistic inputs.
    Space: O(N) for the graph and indegree bookkeeping.
"""

from __future__ import annotations

import heapq
import itertools
import random


def alien_order(words: list[str]) -> str:
    """Return the lexicographically smallest valid alphabet, or ''."""
    if not words:
        return ""

    letters: set[str] = set()
    for word in words:
        letters.update(word)

    graph: dict[str, set[str]] = {letter: set() for letter in letters}
    indegree: dict[str, int] = {letter: 0 for letter in letters}

    for previous, current in zip(words, words[1:]):
        for a, b in zip(previous, current):
            if a != b:
                if b not in graph[a]:        # one edge per pair, no double counts
                    graph[a].add(b)
                    indegree[b] += 1
                break                        # only the FIRST difference is meaningful
        else:
            # current is a prefix of previous (e.g. "cabz" before "cab"):
            # no order information, nothing to do
            pass

    heap = [letter for letter, degree in indegree.items() if degree == 0]
    heapq.heapify(heap)
    order: list[str] = []

    while heap:
        letter = heapq.heappop(heap)
        order.append(letter)
        for nxt in graph[letter]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(heap, nxt)

    if len(order) != len(letters):
        return ""                           # a cycle: some letter never reached indegree 0
    return "".join(order)


def _is_valid_order(words: list[str], alphabet: str) -> bool:
    """Brute-force check: does `alphabet` reproduce the word order?"""
    rank = {letter: i for i, letter in enumerate(alphabet)}
    def key(word: str) -> list[int]:
        return [rank[c] for c in word]
    return all(key(a) <= key(b) for a, b in zip(words, words[1:]))


def _all_valid_orders(words: list[str]) -> list[str]:
    """Enumerate every permutation of the letters that satisfies the order."""
    letters = sorted({c for word in words for c in word})
    return [
        "".join(p)
        for p in itertools.permutations(letters)
        if _is_valid_order(words, "".join(p))
    ]


def _tests() -> None:
    # empty input
    assert alien_order([]) == ""

    # single word: no constraints, the word's letters in sorted order
    assert alien_order(["z"]) == "z"
    assert alien_order(["bac"]) == "abc"

    # the documented example: b<a from cba/cab, a<d from adc/dfb, d<c from dfb/cba
    # the forced prefix is b a d c, and the unconstrained f slots in smallest:
    assert alien_order(["adc", "dfb", "cba", "cab"]) == "badcf"

    # one adjacent pair yields exactly one edge, no cycle
    assert alien_order(["ab", "ba"]) == "ab"
    # the case that breaks the naive approach: a real cycle
    assert alien_order(["ab", "ba", "aa"]) == ""
    # a longer cycle hiding among valid edges
    assert alien_order(["xy", "yz", "zx", "xa"]) == ""

    # prefix pairs carry no information: "cab" before "cabb" is fine either way
    assert alien_order(["cab", "cabb"]) == "abc"
    # ...but the reverse is contradictory only if other edges force it;
    # alone it is simply "no information"
    assert alien_order(["cabb", "cab"]) == "abc"

    # lexicographically smallest among the valid answers
    assert alien_order(["ba", "ab", "ba"]) == ""      # b<a from pair 1, a<b from pair 2: cycle
    assert alien_order(["za", "zb", "a"]) == "zab"     # z<a (from zb/a) and a<b (from za/zb)

    # cross-check against brute force on random word lists
    rng = random.Random(20260922)
    for _ in range(300):
        alphabet = rng.sample("abcde", rng.randrange(1, 5))
        rng.shuffle(alphabet)
        true_order = "".join(alphabet)
        words = [
            "".join(rng.choice(true_order) for _ in range(rng.randrange(1, 5)))
            for _ in range(rng.randrange(1, 6))
        ]
        words.sort(key=lambda w: [true_order.index(c) for c in w])
        expected = _all_valid_orders(words)
        got = alien_order(words)
        if expected:
            assert got == min(expected), (words, got, min(expected))
        else:
            assert got == "", (words, got)

    print("alien_order: all tests passed")


if __name__ == "__main__":
    _tests()
