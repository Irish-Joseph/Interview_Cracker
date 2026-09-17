# Interview Cracker

[![Validate](https://github.com/Irish-Joseph/interview-cracker/actions/workflows/validate-registry.yml/badge.svg)](https://github.com/Irish-Joseph/interview-cracker/actions/workflows/validate-registry.yml)

**Everything you need to prepare for a software engineering interview, in one
repository — explained, worked through, and runnable.**

Most interview repositories are a wall of unexplained solutions. This one is
built around *why* an answer is right: every question has a written answer, every
challenge has a commented solution with its complexity, and every concept links
to a small runnable program you can actually execute.

---

## Start here

| I want to… | Go to |
|---|---|
| **Revise a subject** — data structures, algorithms, SQL, OS, networking, system design | [`interview-prep/`](interview-prep/) |
| **Practise problems** — grouped by the pattern that solves them | [`coding-challenges/`](coding-challenges/) |
| **Do one problem a day** | [`daily-challenges/`](daily-challenges/) |
| **Learn a language feature** — 126 runnable examples across 13 languages | [`examples/`](examples/) |
| **Print or read offline** | [`resources/pdf/`](resources/) |
| **Follow a study plan** — one week or four weeks | [`interview-prep/README.md`](interview-prep/README.md) |

---

## Layout

```
interview-cracker/
│
├── interview-prep/          Question banks with written answers, by subject
│   ├── data-structures/       arrays, linked lists, stacks/queues/heaps,
│   │                          hash tables, trees and graphs
│   ├── algorithms/            complexity, sorting/searching, recursion, DP
│   ├── databases/             SQL queries, indexing, transactions
│   ├── core-cs/               operating systems, networking, concurrency
│   ├── system-design/         fundamentals + a full worked walkthrough
│   ├── languages/             Python, JavaScript, Java
│   └── behavioral/            STAR method and the recurring questions
│
├── coding-challenges/       Problems grouped by SOLVING PATTERN, with
│   ├── two-pointers/          tested solutions and complexity analysis
│   ├── sliding-window/
│   ├── hashing/
│   ├── binary-search/
│   ├── stack/
│   ├── linked-list/
│   ├── trees/
│   ├── graphs/
│   ├── dynamic-programming/
│   └── intervals/
│
├── daily-challenges/        One dated problem per day, answer collapsed
│
├── examples/                126 runnable examples, one concept per file
│   ├── python/  javascript/  typescript/  java/  c/  cpp/  csharp/
│   └── go/  rust/  sql/  bash/  powershell/  ruby/
│
├── resources/pdf/           Printable PDFs generated from interview-prep/
├── scripts/                 Registry validation, test runner, PDF builder
│
├── TOPICS.md                Every example: date, difficulty, category
└── progress.json            The same registry, machine-readable
```

---

## How to use this repository

**If your interview is months away**, work through `interview-prep/` one subject
at a time and do the linked challenges as you go.

**If your interview is next week**, start with
[`interview-prep/README.md`](interview-prep/README.md), which has a one-week and
a four-week plan, then drill `coding-challenges/` by pattern.

**If you have 20 minutes a day**, do that day's
[`daily-challenges/`](daily-challenges/) problem.

The honest advice: recognising the *pattern* beats memorising solutions. Ten
problems understood deeply will serve you better than a hundred skimmed.

---

## What makes this different

- **Every code snippet has been executed.** Solutions are cross-checked against
  brute-force references on randomised inputs, not just eyeballed.
- **Complexity is stated and justified**, including the space cost of recursion.
- **Trade-offs over rules.** Where there is no single right answer — 301 vs 302,
  greedy vs DP, `orElse` vs `orElseGet` — the answer explains the choice.
- **No fake company attributions.** Nothing here claims to be "asked at Google".
  Those claims are not verifiable, and drilling a rumoured list is worse practice
  than understanding the topic.

## Verify it yourself

```bash
python scripts/validate_registry.py    # registries and README agree
python scripts/run_challenges.py       # all 20 challenge test suites
```

Both run on every push and pull request.

---

## Statistics

Examples: 126
Languages: 13
Categories: 97

Plus 19 subject question banks, 20 pattern-grouped challenges, and 8 generated
PDFs. Full per-example listing in [TOPICS.md](TOPICS.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — there is a checklist for each area.
`Skill.md` documents the repository's full maintenance rules.

## Community

- Ask questions in [Q&A Discussions](https://github.com/Irish-Joseph/interview-cracker/discussions/categories/q-a).
- Suggest improvements in [Ideas](https://github.com/Irish-Joseph/interview-cracker/discussions/categories/ideas).
- Request a new question or report a mistake through the issue forms.

If a section helped you, a star makes it easier for the next person to find.
