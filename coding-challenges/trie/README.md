# Pattern: Trie (Prefix Tree)

A tree keyed by character, where a word's letters spell out the path from the
root. Words sharing a prefix share the nodes for that prefix.

## When to reach for it

The decisive signal is **prefix**. If the problem says *starts with*,
*autocomplete*, *common prefix*, or *search with wildcards*, a hash map cannot
help and a trie can.

- Autocomplete and type-ahead
- "Do any stored words start with X?"
- Longest common prefix across a set
- Word-search grids, where you prune a path the moment it stops being a prefix
- Spell-checking, IP routing tables

## Why not just a hash map?

A hash map finds a **whole key** in O(1), and that is all it can do. Hashing
deliberately destroys the relationship between similar keys, so `"pre"` and
`"prefix"` land in unrelated buckets. Answering "all words starting with `pre`"
would mean scanning every key.

A trie keeps that relationship in its structure:

| | Hash map | Trie |
|---|---|---|
| Exact lookup | O(1) average | O(k), k = key length |
| Prefix query | **O(total keys)** | **O(k + matches)** |
| Worst case | O(n) on collisions | O(k), always |
| Memory | one entry per key | one node per distinct prefix character |

A trie's lookup cost does not depend on how many words are stored — only on
how long the key is. That is unusual and worth saying in an interview.

## The shape

```python
class TrieNode:
    def __init__(self):
        self.children = {}        # char -> TrieNode
        self.is_word = False      # does a word END here?
```

`is_word` is the part people forget. Without it you cannot tell a stored word
from a mere prefix of one: after inserting `"apple"`, a search for `"app"` must
return False, but the path exists either way.

## Cost

- **Time:** O(k) for insert, search and prefix-search, for a key of length k.
- **Space:** O(total characters) worst case. Shared prefixes are the saving,
  so tries pay off on dense vocabularies and waste memory on sparse ones.

For a large alphabet, a dict of children beats a fixed 26-slot array unless the
trie is nearly full — most nodes have very few children.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [implement_trie.py](implement_trie.py) | 🟡 Medium | insert / search / startsWith |
| [word_search.py](word_search.py) | 🔴 Hard | Trie + board DFS with prefix pruning |
