# Interview Cracker

[![Validate](https://github.com/Irish-Joseph/interview-cracker/actions/workflows/validate-registry.yml/badge.svg)](https://github.com/Irish-Joseph/interview-cracker/actions/workflows/validate-registry.yml)

**Everything you need to prepare for a software engineering interview, in one
repository — explained, worked through, and runnable.**

Most interview repositories are a wall of unexplained solutions. This one is
built around *why* an answer is right: every question has a written answer, every
challenge has a commented solution with its complexity, and every concept links
to a small runnable program you can actually execute.

---

## What is inside

| Section | What it gives you |
|---|---|
| [`interview-prep/`](interview-prep/) | Subject-by-subject question banks with full written answers — data structures, algorithms, databases, OS, networking, concurrency, system design, language-specific and behavioural. |
| [`coding-challenges/`](coding-challenges/) | Small coding problems grouped by the **pattern** that solves them, each with a tested solution and complexity analysis. |
| [`daily-challenges/`](daily-challenges/) | One focused problem per day, with the answer kept in the same file so you can self-check after attempting it. |
| Language folders (`python/`, `go/`, `rust/`, …) | The original library of focused, runnable examples — one concept per file, across 13 languages. |
| [`resources/`](resources/) | Printable [PDF question banks](resources/pdf/interview-questions-complete.pdf) generated from the Markdown sources. |

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

## Statistics

Examples: 126
Languages: 13
Categories: 97

## Languages Covered

| Language | Examples |
|---|---|
| python | 17 |
| sql | 12 |
| go | 11 |
| javascript | 11 |
| rust | 11 |
| bash | 10 |
| c | 10 |
| java | 10 |
| typescript | 10 |
| cpp | 9 |
| csharp | 9 |
| ruby | 4 |
| powershell | 2 |

Full per-example listing (with date, difficulty and category) is in [TOPICS.md](TOPICS.md).

---

## Repository layout

- `interview-prep/` — question banks with answers, organised by subject.
- `coding-challenges/` — problems grouped by solving pattern, with solutions.
- `daily-challenges/` — one dated problem per day.
- `resources/pdf/` — generated PDF question banks.
- One top-level folder per language, each grouped into categories.
- `TOPICS.md` — human-readable registry of every language example.
- `progress.json` — machine-readable registry of the same.
- `scripts/` — registry validation and the PDF builder.
- `Skill.md` — the maintenance rules this repository follows.

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Community

- Ask questions in [Q&A Discussions](https://github.com/Irish-Joseph/interview-cracker/discussions/categories/q-a).
- Suggest improvements in [Ideas](https://github.com/Irish-Joseph/interview-cracker/discussions/categories/ideas).
- Request a new question or report a mistake through the issue forms.

If a section helped you, a star makes it easier for the next person to find.
