# Interview Cracker Agent Skill

## 1. Mission

Maintain a public GitHub repository that helps people learn programming and
prepare for software engineering interviews.

The repository has four content areas, and this skill maintains **all of them**:

| Area | What it holds |
|---|---|
| `examples/` | Small runnable programs, one concept per file, by language |
| `interview-prep/` | Subject question banks with written answers |
| `coding-challenges/` | Problems grouped by the pattern that solves them |
| `daily-challenges/` | One dated problem per day, answer in a `<details>` block |

Plus three generated artefacts that must be kept in step: the GitHub Pages site
(`docs/`), the PDF question banks (`resources/pdf/`) and the README statistics.

Every run creates **20 items**, each delivered as its own merged pull request.

The goal is NOT commit volume. It is a repository that is genuinely worth
starring: correct, explained, and verifiable.

---

## 2. Absolute Rules

1. Maximum **20 items per calendar day**. Never more.
2. If some items already exist for today, create only the remainder.
3. Stop immediately once today's total reaches 20.
4. Never create a duplicate of existing content.
5. Never overwrite or delete an existing item.
6. Never create empty commits, filler files, or whitespace-only changes.
7. Never backdate commits or rewrite published history.
8. Never force push.
9. Never commit secrets.
10. **Every code snippet published anywhere must be executed or type-checked**
    before it is committed. If no toolchain exists, review it line by line and
    label it `validated by inspection`.
11. Never claim a question is "asked at" a named company.
12. One item = one branch = one pull request = one merge.
13. Never hand-edit a generated artefact (`docs/`, `resources/pdf/`, the
    language table in `examples/README.md`). Regenerate it.
14. If the working tree has unrelated uncommitted changes at startup, STOP and
    report rather than committing or discarding them.

---

## 3. Repository Structure

```text
interview-cracker/
├── README.md              statistics block is generated
├── Skill.md               this file
├── CONTRIBUTING.md
├── TOPICS.md              registry of examples/ only
├── progress.json          same registry, machine-readable
├── LICENSE                MIT
├── .gitattributes         Linguist rules - do not delete (see section 12)
│
├── examples/              <language>/<category>/<descriptive_name>.<ext>
│   └── README.md          GENERATED from progress.json
├── interview-prep/        <subject>/<topic>.md
├── coding-challenges/     <pattern>/<problem>.py  + a README.md per pattern
├── daily-challenges/      YYYY/MM/YYYY-MM-DD.md   + TEMPLATE.md
│
├── docs/                  GENERATED site - never hand-edit
├── resources/pdf/         GENERATED PDFs - never hand-edit
└── scripts/               validators and generators
```

Language folders live **inside `examples/`**, never at the repository root.

---

## 4. The Daily Target

**20 items per day**, spread across all four areas:

| Count | Area | Notes |
|---|---|---|
| **10** | `examples/` | 10 different languages, one concept each |
| **4** | `interview-prep/` | New questions in an existing bank, or a new subject file |
| **4** | `coding-challenges/` | New problems, or a new pattern folder with its README |
| **1** | `daily-challenges/` | Today's dated problem |
| **1** | Housekeeping | Regenerate site + PDFs + statistics (always the 20th) |

This split is the default. Deviate only to keep a neglected area alive, and say
so in the final report. Never deviate by skipping the housekeeping item.

### Difficulty spread

Across the 10 examples, aim for roughly **3 beginner, 5 intermediate,
2 advanced**. Guideline, not a rule.

### Language variety

The 10 examples should use 10 **different** languages, and the combination
should differ from the previous day. Variety never outranks quality — a good
example in a repeated language beats a weak one in a new language.

---

## 5. Startup Procedure

Run these in order, every time, before creating anything.

```bash
cd /d/git_lan_learning
date +%F                       # never assume the date
git status --short --branch    # must be clean
git branch --show-current      # expect: main
git pull --rebase
git log --oneline -20
```

If the working tree is dirty with changes you did not make: **STOP and report.**
Protecting the owner's work outranks the daily target.

Then read, in this order:

1. `TOPICS.md` and `progress.json` — what examples already exist
2. `interview-prep/README.md` — the subject index
3. `coding-challenges/README.md` — the pattern index
4. `daily-challenges/README.md` — the day index
5. Section 6 below — how many items today already has

---

## 6. Resume Protection

The automation may have stopped part-way through: a crash, a lost network, a
closed terminal. **Never assume today's count is zero.**

Only `examples/` has a dated registry. The reliable count across all four areas
is the git history, because every item is exactly one merge into `main`:

```bash
# Items completed today, by area
git log --since="$(date +%F) 00:00" --pretty=%s | grep -c '^learn('
git log --since="$(date +%F) 00:00" --pretty=%s | grep -c '^docs(interview-prep)'
git log --since="$(date +%F) 00:00" --pretty=%s | grep -c '^feat(coding-challenges)'
git log --since="$(date +%F) 00:00" --pretty=%s | grep -c '^feat(daily-challenges)'

# Total today
git log --since="$(date +%F) 00:00" --pretty=%s \
  | grep -cE '^(learn\(|docs\(interview-prep\)|feat\((coding|daily)-challenges\)|chore\(site\))'
```

Cross-check the examples count against the registry:

```bash
python -c "import json;d=json.load(open('progress.json',encoding='utf-8'));\
print(sum(1 for e in d['examples'] if e['date']=='$(date +%F)'))"
```

Then:

```text
remaining = 20 - items_completed_today
```

If `remaining` is 0, **STOP**. Report the state and do nothing else.

Also check for leftovers from an interrupted run:

```bash
gh pr list --state open --json number,title      # an unmerged PR from earlier?
git branch -a | grep "$(date +%F)"               # a branch left behind?
```

Finish an interrupted item before starting a new one.

---

## 7. Choosing Work, and Duplicate Detection

Before creating **every** item, prove it is new.

```bash
# Examples: check both registries and the source tree
grep -i "<concept>" TOPICS.md
python -c "import json;d=json.load(open('progress.json',encoding='utf-8'));\
[print(e['topic']) for e in d['examples'] if e['language']=='<lang>']"
grep -rl "<keyword>" examples/<lang>/

# Prep and challenges: search the prose and the filenames
grep -ril "<concept>" interview-prep/ coding-challenges/ daily-challenges/
```

Use `grep -E` with `|` for alternation — `\|` is literal in `-E` mode and will
silently match nothing, which reads as a false "all clear".

**Keyword hits are not automatically duplicates.** What matters is whether an
existing item *teaches the same thing*. A file that merely mentions `HashMap`
does not block an example about `HashMap`. Compare registered topics, not
incidental words.

If a topic is substantially covered already: **reject it and pick another.**
Renaming, translating to another language, or reformatting does not make a
duplicate original.

### Choosing well

Prefer things people actually search for and get wrong. The best items explain
a **trade-off** or correct a **common misconception** — `omitempty` not working
on a `time.Time`, `BETWEEN` silently dropping timestamps, a class-level
instance variable not being shared with subclasses. A file that only restates
documentation is not worth a commit.

---

## 8. Area Rules: `examples/`

**Path:** `examples/<language>/<category>/<descriptive_name>.<ext>`

Category folders are lowercase kebab-case (`data-structures`, `error-handling`).
Reuse an existing category rather than inventing a near-duplicate; never create
`algorithms/`, `algorithm/` and `algo/` side by side.

Filenames describe what is taught. `binary_search_iterative.py`, never
`example1.py` or `test.py`.

Every file opens with a header giving:

1. The topic, in one line
2. The concepts demonstrated
3. The run/compile command
4. The expected output, or `NOTE: validated by inspection (<reason>)`

Body: roughly 60–200 useful lines. Comments explain *why*, not what — do not
narrate obvious code. End with a block showing the actual output.

**Register every example** in both `TOPICS.md` and `progress.json`, with paths
relative to the repository root (so they start with `examples/`).

---

## 9. Area Rules: `interview-prep/`

**Path:** `interview-prep/<subject>/<topic>.md`

Follow the existing shape exactly:

```markdown
### 🟢 Q. The question, as an interviewer would ask it

**Answer.** The direct answer first, in one or two sentences.

Then the reasoning, a worked example, and the follow-up question that
naturally comes next.
```

Difficulty markers: 🟢 foundational · 🟡 intermediate · 🔴 advanced.

- Lead with the answer. Never make the reader hunt for it.
- Explain the trade-off where there is no single right answer.
- **Run every snippet.** A wrong answer in a revision guide is worse than none.
- Never attribute a question to a named company.
- Add new files to the table in `interview-prep/README.md`.

---

## 10. Area Rules: `coding-challenges/`

**Path:** `coding-challenges/<pattern>/<problem>.py`

Organised by the **pattern that solves it**, not by data structure. A new
pattern folder needs a `README.md` stating *when to reach for it* — the signal
in a problem statement that should bring it to mind.

Every file is runnable and self-testing:

```python
"""
Challenge:  <name>
Pattern:    <pattern>
Difficulty: Easy | Medium | Hard

PROBLEM      - what to return
EXAMPLES     - input -> output, with a brief why
CONSTRAINTS  - sizes, ranges, what is disallowed
HINT         - points at the insight WITHOUT giving the code
COMPLEXITY   - time and space, each justified
"""

def solve(...): ...

def _tests() -> None:
    # empty input, single element, and the case that breaks the naive approach
    ...
    print("<name>: all tests passed")

if __name__ == "__main__":
    _tests()
```

Tests must cover the empty input, the single element, and the case that defeats
the obvious approach. **Cross-check against a brute-force reference on
randomised inputs** wherever that is practical — it is the single most
effective way to catch a wrong solution.

`python scripts/run_challenges.py` must pass in full before committing.

---

## 11. Area Rules: `daily-challenges/`

**Path:** `daily-challenges/YYYY/MM/YYYY-MM-DD.md`, one per calendar day.

Copy `daily-challenges/TEMPLATE.md`. Keep the hint and the solution inside
`<details>` blocks so the problem can be read without spoilers.

Required sections: problem, examples, constraints, hint, solution, complexity,
edge cases that matter, and **the common wrong answer** with the input that
exposes it — often the most useful part of the page.

Run the solution before publishing it. Add a row to the index in
`daily-challenges/README.md`.

---

## 12. Generated Artefacts — the 20th Item

These are **generated**. Editing them by hand is always wrong: the next build
overwrites the change, usually silently.

| Artefact | Generator | Source of truth |
|---|---|---|
| `docs/` (the site) | `scripts/build_site.py` | the Markdown in the three prep areas |
| `docs/assets/social-preview.png` | `scripts/build_social_preview.py` | that script |
| `resources/pdf/*.pdf` | `scripts/build_pdfs.py` | `interview-prep/*.md` |
| `examples/README.md` language table | regenerate from `progress.json` | the registry |
| `README.md` statistics block | regenerate from `progress.json` | the registry |

The final item of every day regenerates all of them in one PR:

```bash
python scripts/build_site.py
python scripts/build_social_preview.py
python scripts/build_pdfs.py          # only when interview-prep/ changed
python scripts/validate_registry.py
python scripts/run_challenges.py
```

Then update the three README statistics lines (`Examples:`, `Languages:`,
`Categories:`) and the `examples/README.md` table from `progress.json`.

Commit prefix: `chore(site):`.

### Things in `docs/` that must survive a rebuild

`build_site.py` deletes and recreates `docs/`, so anything that has to live
there is **written by the script**, never placed by hand:

- `googleabab5b3b9673ebec.html` — Search Console verification
- `CNAME` — written when `CUSTOM_DOMAIN` is set
- `.nojekyll`, `robots.txt`, `sitemap.xml`, `search-index.json`

If a future task needs another file at the site root, add it to the generator.

### `.gitattributes` must not be deleted

Linguist treats a top-level `examples/` directory as documentation and would
report the repository as "Python 100%". `.gitattributes` opts it back in and
marks `*.sql` detectable (Linguist types SQL as `data`, not `programming`).

---

## 13. Validation

**Never commit code known to be wrong.** Validate by the strongest means the
host allows.

| Language | Command | Available here |
|---|---|---|
| Python | `python <file>` | ✅ run |
| JavaScript | `node <file>` | ✅ run |
| TypeScript | `node --experimental-strip-types <file>` | ✅ run |
| | `node --experimental-transform-types <file>` | needed for enums, parameter properties |
| Bash | `bash -n <file>` then run | ✅ run |
| SQL | via Python's `sqlite3` | ✅ run |
| PowerShell | `powershell -File <file>` | ✅ run |
| Rust | `rustc --edition 2021 --emit=metadata <file>` | ⚠ type-check only (no MSVC linker) |
| Go, C, C++, Java, C#, Ruby | — | ❌ inspect |

When no toolchain exists, do better than reading it:

- **Port the logic** to a language you can run, and test it against the
  documented cases. This has caught real bugs.
- **Compute every literal** that appears in an expected-output block — string
  lengths, indices, bit patterns, arithmetic. Never eyeball them.
- Check brace balance, unused imports, and that every claim in the header is
  actually demonstrated by the body.

Then label the file `NOTE: validated by inspection (<reason>)` so a reader
knows the difference. **Never claim an example was run when it was not.**

### Two host quirks that waste time

- The Bash tool fails on a heredoc beyond roughly 200 lines / 8 KB and writes
  nothing. Split long files into a `cat >` plus one or more `cat >>` calls.
- The Bash tool collapses `\` to `\`. A lone `\n` passes through fine, so
  ordinary code is safe; the trap is an embedded string that needs a *literal*
  backslash. Build those from `chr(92)`, or patch line-wise.
- The Windows console is cp1252. Printing `✓`, `⚠` or emoji from a script
  crashes it. Write such output to a file instead.

---

## 14. Delivery: One Item, One Pull Request

Every item is branched from the **current** `main`, merged, and only then is
the next item started. Sequential, never stacked.

```bash
# 1. Always start from up-to-date main
git checkout main && git pull --rebase

# 2. Branch
git checkout -b learn/2026-09-21-03-rust-iterators

# 3. Create and validate the item (sections 8-11, 13)

# 4. Register it (examples only: TOPICS.md + progress.json)

# 5. Stage ONLY the intended files - never `git add .`
git add examples/rust/iterators/foo.rs TOPICS.md progress.json
git status --short
git diff --cached          # read it before committing

# 6. Commit
git commit -m "learn(rust): <specific topic>" \
           -m "Co-Authored-By: ..."

# 7. Push and open the PR
git push -u origin learn/2026-09-21-03-rust-iterators
gh pr create --title "<same as commit subject>" --body-file <body> --base main

# 8. Merge, then return to main
gh pr merge <branch> --merge
git checkout main && git pull --rebase
```

### Rules that exist because they were learned the hard way

- **Use `--merge`, never `--squash`**, and never `--delete-branch` while
  another PR still targets the branch. Deleting a base branch **closes** the
  child PR, and GitHub then refuses to reopen it — the only recovery is opening
  a fresh PR. Delete branches at the end of the day instead.
- **Branch from current `main` each time.** Stacked branches invite conflicts
  in `progress.json` and `TOPICS.md`, which every example touches.
- **Never `git commit -m` with a message containing a double quote** from the
  shell; the quoting breaks and the message is silently truncated. Use
  `-F <file>` for anything non-trivial.

### PR body

State what the item teaches, the validation command **and its result**, and
anything notable — a subtlety the file documents, or a bug caught while
writing it. A reviewer should not have to open the diff to know what changed.

### Commit prefixes

| Area | Prefix |
|---|---|
| `examples/` | `learn(<language>):` |
| `interview-prep/` | `docs(interview-prep):` |
| `coding-challenges/` | `feat(coding-challenges):` |
| `daily-challenges/` | `feat(daily-challenges):` |
| Generated artefacts | `chore(site):` |
| A fix to existing content | `fix(<area>):` |

### If a push or merge fails

Stop creating new items. Read the error, diagnose, fix, retry. Do **not** start
the next item while the current one is unmerged, and never resolve a normal
error with `--force`.

---

## 15. Security

Before every commit:

```bash
git status --short
git diff --cached
```

Never commit passwords, API keys, tokens, private keys, `.env` files,
certificates or personal data. If you see one: **STOP**, do not commit, report.

Public proof-of-control markers are different and belong in the repository —
the Search Console verification file works *only* because it is public. Do not
"fix" it by removing it.

`.gitignore` covers `.env*`, `*.pem`, `*.key`, build output and caches.

---

## 16. Quality Gate

Answer all of these before every commit. If any fails, fix it first.

```text
[ ] Genuinely new - registries and source searched
[ ] Teaches one clear thing, and explains WHY
[ ] Executed, type-checked, or honestly labelled as inspected
[ ] Every literal in the expected output was computed, not guessed
[ ] Complexity claims are correct
[ ] Edge cases covered: empty, single, and the case that breaks the naive way
[ ] Correct area, correct folder, descriptive filename
[ ] Registered (examples: TOPICS.md + progress.json; others: their index)
[ ] Only intended files staged
[ ] No secrets
[ ] Commit message is specific, with the right prefix
```

---

## 17. Final Verification

After the 20th merge:

```bash
git checkout main && git pull --rebase
git status --short --branch                     # expect clean, in sync

# 20 items today?
git log --since="$(date +%F) 00:00" --pretty=%s \
  | grep -cE '^(learn\(|docs\(interview-prep\)|feat\((coding|daily)-challenges\)|chore\(site\))'

python scripts/validate_registry.py             # registries + README agree
python scripts/run_challenges.py                # every challenge suite passes

# Registered files all exist
python -c "import json,os;d=json.load(open('progress.json',encoding='utf-8'));\
print([e['file'] for e in d['examples'] if not os.path.isfile(e['file'])] or 'all present')"

gh pr list --state open --json number --jq 'length'   # expect 0
```

Then tidy the day's branches:

```bash
for b in $(git ls-remote --heads origin "refs/heads/*$(date +%F)*" | sed 's|.*refs/heads/||'); do
  git push origin --delete "$b"
done
git fetch --prune
```

Confirm the site redeployed:

```bash
gh api repos/Irish-Joseph/Interview_Cracker/pages --jq .status   # built
curl -s -o /dev/null -w "%{http_code}" https://irish-joseph.github.io/Interview_Cracker/
```

---

## 18. Final Report

Report what actually happened. Include, concisely:

- The date, target (20), completed, remaining
- A table of the items: area, topic, and **how each was validated**
- Duplicate topics rejected, and bugs caught before committing
- Anything skipped or deviated from, and why
- Any manual action left for the owner

**If the target was not met, say so plainly.** Never report success for work
that did not happen, and never describe an item as "run" when it was inspected.
A truthful partial report is worth more than a tidy false one.

---

## 19. Priority Order

When rules conflict:

```text
1. Protect the owner's uncommitted work
2. Protect secrets and security
3. Protect published git history
4. Correctness - never publish code known to be wrong
5. Honesty - never overstate what was validated
6. No duplicates
7. Educational value
8. Repository organisation
9. Reaching 20 items
10. Language and area variety
```

Reaching 20 is **ninth**. A day that delivers 14 correct, well-explained items
is a better day than one that delivers 20 with a wrong answer among them.

---

## 20. Autonomy

Decide these independently, without asking:

- Which areas, languages, topics, difficulties, categories and filenames
- The implementation, the validation approach, and the PR text
- Whether a proposed topic is too close to an existing one

Stop and ask the owner only for:

- A dirty working tree containing changes you did not make
- Authentication or permission failures
- A merge conflict needing judgement
- A possible secret exposure
- A missing remote, or repository corruption
- Anything requiring a decision that is genuinely theirs (a licence, a domain,
  deleting their content)

Do **not** ask whether to continue, whether to push, or which topic to pick.
This skill exists so the run is autonomous.

---

## 21. Definition of Success

Not "20 merged PRs".

```text
20 items that are
  unique, useful, correct, validated,
  properly registered, individually reviewed,
  delivered as one merged PR each,
  with the site, PDFs and statistics regenerated to match.
```

After the 20th merge and the final verification: **stop for the day.**
