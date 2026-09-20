"""
Challenge:  Word Ladder
Pattern:    Graphs (implicit graph + BFS for shortest path)
Difficulty: Hard

PROBLEM
-------
Given two words beginWord and endWord and a dictionary wordList, a
transformation sequence changes exactly one letter at a time and every
intermediate word must appear in wordList. Return the number of words in
the SHORTEST transformation sequence, or 0 if no such sequence exists.

EXAMPLES
--------
begin="hit", end="cog", list=["hot","dot","dog","lot","log","cog"]
  -> 5   (hit -> hot -> dot -> dog -> cog)

begin="hit", end="cog", list=["hot","dot","dog","lot","log"]
  -> 0   (endWord not reachable, not even in the list)

begin="hot", end="hot", list=["hot"]
  -> 1   (already there)

CONSTRAINTS
-----------
- 1 <= word length <= 5; all words lowercase; beginWord need NOT be in
  wordList, but endWord MUST be (otherwise answer is 0).
- A BFS is expected: a DFS that memoises visited words still explores in
  the right order only if it tracks depth; plain greedy/DFS is wrong.

HINT
----
The graph is implicit: two words are connected if they differ by exactly
one letter. Instead of building all edges (O(n^2 * L)), for each word try
every single-letter substitution (26 * L candidates) and see if the result
is in the dictionary — an O(1) set lookup. BFS from beginWord counts the
number of words along the way, not the number of edges.

COMPLEXITY
----------
Time:  O(n * L * 26) - each word generates at most 26*L neighbours
Space: O(n * L) - the visited set and the BFS queue
"""

from collections import deque
import string


def word_ladder_length(begin_word: str, end_word: str, word_list: list[str]) -> int:
    if end_word not in word_list:
        return 0

    remaining = set(word_list)
    remaining.discard(begin_word)  # begin need not be in the list

    queue = deque([(begin_word, 1)])  # (word, words-in-sequence-so-far)
    visited = {begin_word}

    while queue:
        word, length = queue.popleft()

        if word == end_word:
            return length

        for i in range(len(word)):
            for letter in string.ascii_lowercase:
                if letter == word[i]:
                    continue
                candidate = word[:i] + letter + word[i + 1:]
                if candidate in remaining:
                    remaining.discard(candidate)  # mark visited on enqueue
                    queue.append((candidate, length + 1))

    return 0


def _tests() -> None:
    # The specified examples.
    words = ["hot", "dot", "dog", "lot", "log", "cog"]
    assert word_ladder_length("hit", "cog", words) == 5

    assert word_ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    assert word_ladder_length("hot", "hot", ["hot"]) == 1

    # endWord not in the list at all.
    assert word_ladder_length("hit", "cog", ["hot", "dot"]) == 0

    # Direct one-step transformation.
    assert word_ladder_length("hot", "dot", ["dot"]) == 2

    # beginWord absent from the list is fine.
    assert word_ladder_length("red", "tax", ["ted", "tex", "rex", "tax"]) == 4

    # begin and end differ by two letters: without an intermediate word
    # in the list there is no ladder, even though endWord is present.
    assert word_ladder_length("ab", "cd", ["cd"]) == 0
    # ...but with "ad" present, the ladder ab -> ad -> cd has 3 words.
    assert word_ladder_length("ab", "cd", ["ad", "cd"]) == 3

    # Cross-check against an explicit-graph BFS reference on small cases.
    import random

    def reference(begin, end, word_list):
        if end not in word_list:
            return 0
        all_words = list(dict.fromkeys([begin] + word_list))
        index = {w: i for i, w in enumerate(all_words)}

        def neighbours(w):
            for j in range(len(w)):
                for c in string.ascii_lowercase:
                    if c != w[j]:
                        cand = w[:j] + c + w[j + 1:]
                        if cand in index:
                            yield index[cand]

        from collections import deque as dq
        dist = {index[begin]: 1}
        q = dq([index[begin]])
        while q:
            u = q.popleft()
            if all_words[u] == end:
                return dist[u]
            for v in neighbours(all_words[u]):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return 0

    random.seed(21)
    for _ in range(120):
        size = random.randint(1, 8)
        words = set()
        for _ in range(size):
            words.add("".join(random.choice("ab") for _ in range(2)))
        word_list = sorted(words)
        begin = "".join(random.choice("ab") for _ in range(2))
        end = random.choice(word_list) if word_list else "zz"
        assert word_ladder_length(begin, end, word_list) == reference(begin, end, word_list), (begin, end, word_list)

    print("word_ladder: all tests passed")


if __name__ == "__main__":
    _tests()
