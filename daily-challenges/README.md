# Daily Challenges

One focused problem per day. Small enough to do before work, hard enough to be
worth doing.

## How it works

Each file has the problem at the top and the **answer collapsed** underneath, in
a `<details>` block. GitHub renders that as a "Show solution" toggle, so you can
read the problem without seeing the answer.

**Do this:**

1. Read the problem and the constraints.
2. Set a 20-minute timer and write the code in your own editor.
3. Stuck at 10 minutes? Expand **Hint** only.
4. Finished, or out of time? Expand **Solution** and compare — especially the
   complexity and the edge cases.

Time-boxing matters more than finishing. An hour of grinding teaches less than
20 minutes followed by reading a good solution.

## Layout

```
daily-challenges/
├── TEMPLATE.md          copy this to add a new day
└── 2026/
    └── 09/
        └── 2026-09-17.md
```

One file per day, named `YYYY-MM-DD.md`, filed under `YYYY/MM/`.

## Index

| Date | Challenge | Difficulty | Pattern |
|---|---|---|---|
| [2026-09-17](2026/09/2026-09-17.md) | Move zeroes to the end, in place | 🟢 Easy | Two pointers |
| [2026-09-18](2026/09/2026-09-18.md) | Product of array except self | 🟡 Medium | Prefix/suffix products |
| [2026-09-19](2026/09/2026-09-19.md) | Find the duplicate number | 🔴 Hard | Floyd's cycle detection |
| [2026-09-20](2026/09/2026-09-20.md) | First unique character in a string | 🟢 Easy | Hash map (count, then scan) |
| [2026-09-21](2026/09/2026-09-21.md) | Next permutation | 🟡 Medium | In-place array manipulation |

## Contributing a day

Copy [`TEMPLATE.md`](TEMPLATE.md), fill it in, and add a row to the index above.
The solution must be correct and its complexity stated honestly — see
[`CONTRIBUTING.md`](../CONTRIBUTING.md).
