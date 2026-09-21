"""
Challenge:  Implement a Trie (Prefix Tree)
Pattern:    Trie
Difficulty: Medium

PROBLEM
-------
Implement a trie supporting:
    insert(word)       add a word
    search(word)       True only if the exact word was inserted
    starts_with(prefix) True if any inserted word begins with prefix

EXAMPLES
--------
insert("apple")
search("apple")       -> True
search("app")         -> False     <- a prefix is not a word
starts_with("app")    -> True
insert("app")
search("app")         -> True      <- now it is

CONSTRAINTS
-----------
- Lowercase letters, though nothing here depends on that.
- All three operations should be O(k) for a key of length k.

HINT
----
Each node holds a map from character to child node. Walking a word means
walking the tree one character at a time.

The whole problem turns on one extra field. After inserting "apple", the path
a-p-p exists, so a naive search for "app" would follow it and report True.
You need to record whether a word ENDS at a node - a boolean per node.

That single flag is the only difference between search() and starts_with():
both walk the same path, but search then asks "is this a word end?" while
starts_with is satisfied by the path existing at all.

COMPLEXITY
----------
Time:  O(k) per operation, INDEPENDENT of how many words are stored
Space: O(total characters inserted) worst case; shared prefixes are the saving
"""


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_word = False        # does a complete word end here?


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            # setdefault creates the child only when it is missing, which is
            # exactly the "share the prefix, branch on divergence" behaviour.
            node = node.children.setdefault(char, TrieNode())
        node.is_word = True

    def _walk(self, text: str) -> TrieNode | None:
        """Follow text from the root; return the node reached, or None."""
        node = self.root
        for char in text:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        # The path existing is not enough - a word must END here.
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        node = self._walk(prefix)
        if node is None:
            return False
        # The path existing is ALMOST enough - but an empty trie has a root
        # with no words under it, so starts_with("") would wrongly say True.
        # A node is only meaningful if a word ends here or continues below.
        # Still O(k): this checks the node reached, not the whole subtree.
        return node.is_word or bool(node.children)

    def words_with_prefix(self, prefix: str) -> list[str]:
        """Every stored word beginning with prefix - what a hash map cannot do."""
        node = self._walk(prefix)
        if node is None:
            return []

        found: list[str] = []

        def collect(current: TrieNode, path: str) -> None:
            if current.is_word:
                found.append(prefix + path)
            for char, child in current.children.items():
                collect(child, path + char)

        collect(node, "")
        return sorted(found)


def _tests() -> None:
    trie = Trie()

    # The defining behaviour: a prefix is not a word until it is inserted.
    trie.insert("apple")
    assert trie.search("apple") is True
    assert trie.search("app") is False, "a prefix must not count as a word"
    assert trie.starts_with("app") is True
    trie.insert("app")
    assert trie.search("app") is True, "now it is a word"

    # Misses
    assert trie.search("banana") is False
    assert trie.starts_with("ban") is False
    assert trie.search("appl") is False
    assert trie.starts_with("appl") is True

    # The empty string, on an EMPTY trie. This is the case that a naive
    # "does the path exist?" implementation gets wrong: the root always
    # exists, but with nothing stored, nothing has any prefix.
    fresh = Trie()
    assert fresh.starts_with("") is False, "no words stored, so no prefixes"
    assert fresh.search("") is False
    fresh.insert("")
    assert fresh.search("") is True
    assert fresh.starts_with("") is True

    # And once any word exists, the empty prefix matches it.
    nonempty = Trie()
    nonempty.insert("a")
    assert nonempty.starts_with("") is True

    # Duplicate inserts are idempotent.
    dup = Trie()
    dup.insert("dog")
    dup.insert("dog")
    assert dup.search("dog") is True

    # A word that is a strict prefix of another, inserted in both orders.
    for order in (["car", "card"], ["card", "car"]):
        t = Trie()
        for w in order:
            t.insert(w)
        assert t.search("car") is True and t.search("card") is True, order
        assert t.search("ca") is False, order

    # Prefix collection - the thing a hash map cannot do.
    auto = Trie()
    for w in ["prefix", "pre", "prepare", "press", "python"]:
        auto.insert(w)
    assert auto.words_with_prefix("pre") == ["pre", "prefix", "prepare", "press"]
    assert auto.words_with_prefix("pref") == ["prefix"]
    assert auto.words_with_prefix("zz") == []
    assert sorted(auto.words_with_prefix("")) == ["pre", "prefix", "prepare", "press", "python"]

    # Cross-check every operation against plain sets on random vocabularies.
    import random
    import string

    random.seed(97)
    for _ in range(300):
        words = {
            "".join(random.choices(string.ascii_lowercase[:4], k=random.randint(0, 5)))
            for _ in range(random.randint(0, 12))
        }
        t = Trie()
        for w in words:
            t.insert(w)

        # Probe with both stored and unstored strings.
        probes = list(words) + [
            "".join(random.choices(string.ascii_lowercase[:5], k=random.randint(0, 5)))
            for _ in range(8)
        ]
        for probe in probes:
            assert t.search(probe) == (probe in words), (sorted(words), probe)
            expected_prefix = any(w.startswith(probe) for w in words)
            assert t.starts_with(probe) == expected_prefix, (sorted(words), probe)
            assert t.words_with_prefix(probe) == sorted(
                w for w in words if w.startswith(probe)
            ), (sorted(words), probe)

    print("implement_trie: all tests passed (300 randomised vocabularies)")


if __name__ == "__main__":
    _tests()
