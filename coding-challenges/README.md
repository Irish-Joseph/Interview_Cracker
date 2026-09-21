# Coding Challenges

Problems grouped by the **pattern that solves them**, not by difficulty or by
data structure. Recognising the pattern is the transferable skill; an individual
problem is not.

## How to use these

1. Read the pattern's `README.md` first — it tells you what signal in a problem
   statement means "use this pattern".
2. Open a challenge and read **only** down to the `HINT` line.
3. Give yourself 20 minutes on a blank file. Write the code before running it.
4. Stuck at 20 minutes? Read the hint, not the solution.
5. Compare with the solution — including the complexity section.

Every file is runnable and self-testing:

```bash
python coding-challenges/two-pointers/valid_palindrome.py
```

Run the whole suite:

```bash
python scripts/run_challenges.py
```

## Patterns

| Pattern | Use it when | Challenges |
|---|---|---|
| [trie](trie/) | Anything prefix-shaped: autocomplete, "starts with", word search | Implement a trie |
| [two-pointers](two-pointers/) | Sorted array; find a pair/triplet; filter in place | Valid palindrome, 3Sum |
| [sliding-window](sliding-window/) | Longest/shortest **contiguous** run satisfying a rule | Longest unique substring, max sum of size k |
| [hashing](hashing/) | You are searching inside a loop | Two sum, group anagrams |
| [binary-search](binary-search/) | Sorted input, or a monotonic yes/no over a numeric range | Search rotated array, minimum eating speed |
| [backtracking](backtracking/) | You need **all** arrangements — every subset, permutation or valid board | Subsets, combination sum |
| [heap](heap/) | Top-K, Kth largest, a running median, or merging k sorted streams | Top K frequent elements |
| [prefix-sum](prefix-sum/) | Many range-sum queries, or counting subarrays that sum to k | Subarray sum equals k |
| [stack](stack/) | Matching pairs; "next greater/smaller element" | Valid parentheses, daily temperatures |
| [linked-list](linked-list/) | Pointer rewiring; fast/slow traversal | Reverse a list, detect a cycle |
| [trees](trees/) | Recursive structure; level-by-level work | Level-order traversal, validate a BST |
| [graphs](graphs/) | Connectivity, shortest hops, dependency order | Number of islands, course schedule |
| [union-find](union-find/) | Edges arrive over time; "are these connected yet?"; cycles in an undirected graph | Redundant connection |
| [dynamic-programming](dynamic-programming/) | Overlapping subproblems; count/min/max | Climbing stairs, coin change |
| [intervals](intervals/) | Ranges that may overlap | Merge intervals, meeting rooms |

## Difficulty

🟢 Easy · 🟡 Medium · 🔴 Hard — the label reflects the *insight* required, not the
amount of code.

## A note on these problems

These are long-standing, widely-known problems that appear in textbooks, courses
and practice sites. They are here because the underlying pattern is genuinely
worth knowing, not because any company is claimed to ask them.
