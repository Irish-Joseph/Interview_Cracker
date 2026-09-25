<div align="center">

# Interview Cracker

**Learn the pattern. Explain the trade-off. Run the code.**

[![Validate](https://github.com/Irish-Joseph/Interview_Cracker/actions/workflows/validate-registry.yml/badge.svg)](https://github.com/Irish-Joseph/Interview_Cracker/actions/workflows/validate-registry.yml)
[![GitHub Pages](https://img.shields.io/badge/read-searchable_site-22c55e?logo=github)](https://irish-joseph.github.io/Interview_Cracker/)
[![License: MIT](https://img.shields.io/badge/license-MIT-06b6d4.svg)](LICENSE)

<img src="assets/interview-cracker-hero.png" alt="A focused coding workspace with a visual path through code, algorithms, databases, and interview readiness" width="100%">

203 runnable examples · 54 coding challenges · 34 interview guides · 13 languages

Examples: 203

Languages: 13

Categories: 134

[Start a study plan](interview-prep/README.md) · [Solve today's challenge](daily-challenges/2026/09/2026-09-25.md) · [Browse the website](https://irish-joseph.github.io/Interview_Cracker/)

</div>

## Pick your path

| Your goal | Start here | What you get |
|---|---|---|
| Prepare for an interview | [Interview prep](interview-prep/) | Answer-first guides for DSA, databases, core CS, system design, languages, and behavioral rounds |
| Learn problem-solving patterns | [Coding challenges](coding-challenges/) | Self-testing Python problems grouped by the pattern that solves them |
| Build a daily habit | [Daily challenges](daily-challenges/) | One dated problem, with the hint and solution hidden until you need them |
| Learn by running code | [Examples](examples/) | Small programs across 13 languages, one concept per file |
| Study offline | [PDF library](resources/pdf/) | Generated, printable interview question banks |

## Today's learning pack — 24 September 2026

- **Daily challenge:** [Longest Valid Parentheses](daily-challenges/2026/09/2026-09-24.md)
- **New patterns:** sliding-window maximum, binary-search boundaries, permutations, and tree depth
- **Interview depth:** cache stampedes, covering indexes, virtual-memory faults, and selection algorithms
- **Language traps:** mutable defaults, cancellation, branded types, suppressed exceptions, UPSERTs, and more

## A practical study loop

```text
Learn a concept  →  Recognize its pattern  →  Solve without hints
       ↑                                         ↓
Review the trade-offs  ←  Test edge cases  ←  Explain it aloud
```

1. Pick one topic from [interview prep](interview-prep/README.md).
2. Attempt a related [challenge](coding-challenges/README.md) for 20 minutes.
3. Run the tests, then compare complexity and edge cases.
4. Re-attempt from a blank file a day later.

The repository favors understanding over memorization: solutions explain why
they work, what breaks the obvious approach, and where the trade-offs change.

## Repository map

```text
Interview_Cracker/
├── interview-prep/      answer-first revision guides and study plans
├── coding-challenges/   50 tested problems grouped by solving pattern
├── daily-challenges/    one spoiler-safe challenge per day
├── examples/            193 focused programs across 13 languages
├── resources/pdf/       generated offline question banks
├── docs/                generated searchable GitHub Pages site
├── scripts/             validation and build tools
├── TOPICS.md             human-readable example index
└── progress.json         machine-readable example registry
```

## Quality you can verify

- Runnable code is executed or type-checked when the toolchain is available.
- Challenge suites cover edge cases and use randomized brute-force checks where practical.
- Complexity claims include the reason, not only the notation.
- No unverifiable “asked at company X” claims.

```bash
python scripts/validate_registry.py
python scripts/run_challenges.py
```

Both checks run in CI. The searchable site and PDFs are generated from the same
Markdown sources, so the repository remains the source of truth.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the content checklist and
[Skill.md](Skill.md) for repository maintenance rules. New examples must be
focused, registered, and honestly labeled with how they were validated.

## Community and license

Ask questions in [Discussions](https://github.com/Irish-Joseph/Interview_Cracker/discussions/categories/q-a), suggest an improvement in [Ideas](https://github.com/Irish-Joseph/Interview_Cracker/discussions/categories/ideas), or open an issue for a correction.

[MIT](LICENSE) — use it, fork it, and teach from it. If it helps your preparation,
a star helps the next learner find it too.
