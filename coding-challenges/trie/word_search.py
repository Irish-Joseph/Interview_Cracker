"""
Challenge:  Word Search (words on a grid)
Pattern:    Trie + DFS (build the dictionary once, search the board once)
Difficulty: Hard

PROBLEM
    Given a grid of letters and a dictionary of words, return every word
    from the dictionary that can be read on the board by moving
    horizontally or vertically to adjacent cells, without reusing a cell
    within a single word.

EXAMPLES
    board = [["o","a","a","n"],
             ["e","t","a","e"],
             ["i","h","k","r"],
             ["i","f","l","v"]],
    words = ["oath","pea","eat","rain"]  -> ["eat", "oath"]

    board = [["a"]], words = ["a"]       -> ["a"]
    board = [["a"]], words = ["b"]       -> []

CONSTRAINTS
    - Grid up to 30x30; dictionary up to 10^4 words of length up to 10.
    - A brute force that, for every word, DFSes the whole board is
      exponential in BOTH directions and fails the limit - the trie exists
      to prune the search to prefixes that are in the dictionary at all.

HINT
    Build one trie of the dictionary. DFS the board; at each cell, follow the
    trie pointer - if it is None, this path matches no dictionary prefix, so
    prune the whole subtree. Mark the cell used with a board mutation (or a
    visited set) and undo it on the way back up. When a node marks the end of
    a word, record it (and delete that node so the same word is not found
    twice).

COMPLEXITY
    Time: O(B * 4^W) in the worst case where B is the number of cells and W
          the longest word - but the trie makes the constant tiny in practice,
          because any path that is not a dictionary prefix dies immediately.
    Space: O(D) for the trie (D = total letters in the dictionary) plus O(W)
          recursion depth.
"""

from __future__ import annotations

import random

Cell = list[str]


class _TrieNode:
    __slots__ = ("children", "is_end", "word")

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.is_end = False
        self.word: str | None = None


def _build_trie(words: list[str]) -> _TrieNode:
    root = _TrieNode()
    for word in words:
        node = root
        for ch in word:
            node = node.children.setdefault(ch, _TrieNode())
        node.is_end = True
        node.word = word
    return root


def _search(board: Cell, rows: int, cols: int, r: int, c: int,
            node: _TrieNode, found: list[str]) -> None:
    ch = board[r][c]
    nxt = node.children.get(ch)
    if nxt is None:
        return                              # not a dictionary prefix: prune

    if nxt.is_end:
        found.append(nxt.word)
        nxt.is_end = False                   # found once is enough
        nxt.word = None

    # Mark used, explore, unmark - the board mutation IS the visited set.
    board[r][c] = "\0"
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "\0":
            _search(board, rows, cols, nr, nc, nxt, found)
    board[r][c] = ch


def word_search(board: Cell, words: list[str]) -> list[str]:
    if not board or not board[0] or not words:
        return []

    rows, cols = len(board), len(board[0])
    root = _build_trie(list(dict.fromkeys(words)))   # de-dup, keep order
    found: list[str] = []

    work = [row[:] for row in board]                 # never mutate the caller's board
    for r in range(rows):
        for c in range(cols):
            _search(work, rows, cols, r, c, root, found)

    return sorted(found)


def _tests() -> None:
    # empty board / empty dictionary
    assert word_search([], ["a"]) == []
    assert word_search([["a"]], []) == []

    # single cell, hit and miss
    assert word_search([["a"]], ["a"]) == ["a"]
    assert word_search([["a"]], ["b"]) == []
    assert word_search([["a"]], ["aa"]) == []        # needs two cells

    # the documented example
    board: Cell = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    assert word_search(board, ["oath", "pea", "eat", "rain"]) == ["eat", "oath"]

    # the input must not be mutated
    snapshot = [row[:] for row in board]
    word_search(board, ["oath"])
    assert board == snapshot

    # a word that requires revisiting the same cell via DIFFERENT routes
    # must be found once only, and a word using a cell twice is invalid:
    assert word_search([["a", "a"], ["a", "a"]], ["aaaa"]) == ["aaaa"]
    assert word_search([["a", "a"], ["a", "a"]], ["aaaaa"]) == []   # only 4 cells

    # cross-check against a brute force on small random boards
    rng = random.Random(20260923)
    letters = "ab"
    for _ in range(300):
        rows = cols = rng.randrange(1, 4)
        rb: Cell = [[rng.choice(letters) for _ in range(cols)] for _ in range(rows)]
        # build a dictionary: some real walkable words, some random junk
        words: list[str] = []
        for _ in range(rng.randrange(0, 6)):
            length = rng.randrange(1, 5)
            if rng.random() < 0.5:
                # a genuine random walk on the board
                r, c = rng.randrange(rows), rng.randrange(cols)
                w = [rb[r][c]]
                used = {(r, c)}
                for _ in range(length - 1):
                    options = [(r + dr, c + dc)
                               for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                               if 0 <= r + dr < rows and 0 <= c + dc < cols
                               and (r + dr, c + dc) not in used]
                    if not options:
                        break
                    r, c = rng.choice(options)
                    used.add((r, c))
                    w.append(rb[r][c])
                words.append("".join(w))
            else:
                words.append("".join(rng.choice(letters) for _ in range(length)))

        def brute() -> set[str]:
            import itertools
            out = set()
            for w in set(words):
                for sr in range(rows):
                    for sc in range(cols):
                        if _dfs_brute(rb, rows, cols, sr, sc, w, 0):
                            out.add(w)
                            break
            return out

        assert set(word_search(rb, words)) == brute(), (rb, words)

    print("word_search: all tests passed")


def _dfs_brute(board: Cell, rows: int, cols: int, r: int, c: int,
               word: str, i: int) -> bool:
    if board[r][c] != word[i]:
        return False
    if i == len(word) - 1:
        return True
    old = board[r][c]
    board[r][c] = "\0"
    ok = False
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "\0" \
                and _dfs_brute(board, rows, cols, nr, nc, word, i + 1):
            ok = True
            break
    board[r][c] = old
    return ok


if __name__ == "__main__":
    _tests()
