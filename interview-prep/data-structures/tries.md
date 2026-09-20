# Tries & Prefix Data Structures

A trie (prefix tree) stores strings so that shared prefixes are stored
once. It is the go-to structure when the question mentions "prefix",
"autocomplete", or "dictionary word" — and it is the backbone of command
completion, spell-checking, and routing tables.

---

### 🟢 Q. What is a trie, and what does it buy you over a hash set of words?

**Answer.** A trie is a tree where each edge is labelled with a character
and a path from the root spells a string. What it buys you is **prefix
awareness**: `search`, `insert`, and `starts_with` all cost O(L) in the
string length L (not the number of words), and you can enumerate every
word with a given prefix by walking the subtree — something a hash set
cannot do at all.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def _walk(self, s: str):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

t = Trie()
for w in ["cat", "car", "card", "care"]:
    t.insert(w)
assert t.search("cat") and t.search("card") and not t.search("ca")
assert t.starts_with("car") and not t.starts_with("dog")
```

The key detail: `search("ca")` is False even though `starts_with("ca")` is
True, because `ca` is a prefix but was never itself inserted — the `is_end`
flag distinguishes "a word ends here" from "a path passes through here".

---

### 🟡 Q. How do you list all words that share a prefix, and what's the cost?

**Answer.** Walk to the node for the prefix (O(L)), then a DFS of that
subtree collecting every `is_end` node. The cost is O(L + K) where K is
the total number of characters in all matching words — you pay for the
output, which is unavoidable.

```python
def words_with_prefix(self, prefix: str) -> list[str]:
    node = self._walk(prefix)
    if node is None:
        return []
    out = []
    def dfs(n, acc):
        if n.is_end:
            out.append(prefix + acc)
        for ch in sorted(n.children):
            dfs(n.children[ch], acc + ch)
    dfs(node, "")
    return out

t.words_with_prefix("ca")   # ['car', 'card', 'care', 'cat']
t.words_with_prefix("do")   # []
```

This is exactly the autocomplete step. Note the `sorted(...)` makes the
output deterministic (alphabetical); drop it if you only care about
existence and want to stop early.

---

### 🟡 Q. Trie vs sorted array + binary search vs hash set — when is each right?

**Answer.**

| Need | Best fit | Why |
|---|---|---|
| "Is this exact word present?" | Hash set | O(L) expected, tiny constant |
| "Any word with this prefix?" | Trie | Subtree walk; the other two can't |
| "Nearest word / suggest close match" | Trie | DFS with a small edit budget |
| Memory is tight, no prefix queries | Sorted array | No per-node object overhead |

A hash set wins on plain membership and uses far less memory. A trie's
cost is one node object per distinct prefix, so a dictionary of 100k long
words can be memory-heavy — which is why production systems often use a
**radix trie** (compress unary chains into a single labelled edge) or a
sorted array with binary search when they don't actually need prefix
enumeration.

---

### 🔴 Q. How would you implement "longest word in the dict that is a
prefix of `s`", and what's the complexity?

**Answer.** Insert every dictionary word into a trie, then walk `s`
character by character, tracking the deepest `is_end` node you pass.
When the walk falls off a branch, stop — you've found the longest prefix
that exists. Time is O(L + total dict characters) to build plus O(L) to
query; space O(total dict characters).

```python
def longest_prefix(trie: "Trie", s: str) -> str:
    node = trie.root
    best = ""
    for i, ch in enumerate(s):
        if ch not in node.children:
            break
        node = node.children[ch]
        if node.is_end:
            best = s[: i + 1]
    return best

t = Trie()
for w in ["we", "word", "flower", "flowering"]:
    t.insert(w)
assert longest_prefix(t, "flowerpowers") == "flower"
assert longest_prefix(t, "dog") == ""
```

The trap is returning the last *matched character* instead of the last
position where a **complete word** ended — "flowe" walks fine but isn't a
word, so `is_end` is what makes the answer "flower", not "flowe".

---

### 🟢 Q. Why do we mark a terminal node instead of, say, storing the word?

**Answer.** Storing the full word at each terminal node would duplicate
every prefix's characters and blow the space from O(total characters) to
O(total characters × average length). A single boolean `is_end` marks the
end of a word while the shared path still holds each character exactly
once. If you do need the actual string (e.g. to return it), reconstruct it
from the path during the walk — that's what `prefix + acc` does in the
DFS above — rather than storing copies.
