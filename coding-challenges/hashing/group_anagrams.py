"""
Challenge:  Group Anagrams
Pattern:    Hashing (canonical key)
Difficulty: Medium

PROBLEM
-------
Given a list of strings, group together the ones that are anagrams of each
other (same letters, any order).

EXAMPLES
--------
["eat", "tea", "tan", "ate", "nat", "bat"]
  -> [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]

CONSTRAINTS
-----------
- Lowercase letters.
- The order of the groups does not matter, but keep the original order of
  the words inside each group (this implementation does).

HINT
----
Comparing every pair of words is O(n^2 * k). Instead, find a *canonical form*
that is identical for all anagrams of each other and different otherwise - then
words with the same canonical form land in the same bucket of a hash map.

Sorting each word's letters is the simplest such form. A tuple of 26 letter
counts is another, and is asymptotically faster.

COMPLEXITY
----------
Time:  O(n * k log k) for n words of length k (the sort dominates)
       O(n * k) with the letter-count key instead
Space: O(n * k) for the groups
"""

from collections import defaultdict


def group_anagrams(words: list[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)

    for word in words:
        # Anagrams share the same sorted letters: "eat" and "tea" -> "aet".
        key = "".join(sorted(word))
        groups[key].append(word)

    return list(groups.values())


def group_anagrams_by_counts(words: list[str]) -> list[list[str]]:
    """Same idea, O(k) per word instead of O(k log k).

    The key is a 26-tuple of letter counts. A tuple is hashable; a list is not.
    """
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)

    for word in words:
        counts = [0] * 26
        for char in word:
            counts[ord(char) - ord("a")] += 1
        groups[tuple(counts)].append(word)

    return list(groups.values())


def _tests() -> None:
    def normalise(result: list[list[str]]) -> list[list[str]]:
        """Group order is unspecified, so sort before comparing."""
        return sorted(sorted(group) for group in result)

    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    expected = [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
    assert normalise(group_anagrams(words)) == expected
    assert normalise(group_anagrams_by_counts(words)) == expected

    assert group_anagrams([]) == []
    assert group_anagrams([""]) == [[""]]
    assert group_anagrams(["a"]) == [["a"]]
    assert normalise(group_anagrams(["abc", "cba", "xyz"])) == [["abc", "cba"], ["xyz"]]

    # Words within a group keep their input order.
    assert group_anagrams(["tea", "eat", "ate"]) == [["tea", "eat", "ate"]]

    # Repeated identical words group together.
    assert group_anagrams(["ab", "ab"]) == [["ab", "ab"]]

    # Both implementations must always agree.
    import random
    import string

    random.seed(23)
    for _ in range(200):
        sample = [
            "".join(random.choices(string.ascii_lowercase[:4], k=random.randint(0, 5)))
            for _ in range(random.randint(0, 8))
        ]
        assert normalise(group_anagrams(sample)) == normalise(group_anagrams_by_counts(sample)), sample

    print("group_anagrams: all tests passed (200 randomised cases, both variants)")


if __name__ == "__main__":
    _tests()
