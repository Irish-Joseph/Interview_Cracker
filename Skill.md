# Interview Cracker Agent Skill

## 1. Mission

Maintain a public GitHub repository that helps developers learn programming
concepts and prepare for software engineering interviews.

The repository has two halves:

1. **The daily example library** - small, focused, runnable programs, one
   concept per file, organised by language. This is what the daily target below
   refers to, and its rules are unchanged.
2. **The interview sections** - `interview-prep/`, `coding-challenges/`,
   `daily-challenges/` and `resources/`. These are NOT part of the daily
   12-example target. See section 3a.

Every day, the agent must create exactly **12 new educational code examples**.

Each example must:

- Be genuinely useful.
- Teach a clear programming concept.
- Be different from every existing example.
- Be placed in the correct programming-language folder.
- Be validated when possible.
- Be committed separately.
- Be pushed separately.

Daily target:

```text
12 new educational examples
12 commits
12 successful pushes
```

The goal is NOT to generate meaningless commits, duplicate programs, empty commits, or artificial Git activity.

---

# 2. Absolute Rules

The agent MUST follow these rules.

1. Create a maximum of 12 new examples per calendar day.
2. Never intentionally create more than 12 examples for the same day.
3. Never create duplicate examples.
4. Never overwrite an existing educational example.
5. Never create empty commits.
6. Never modify Git commit dates to create historical contributions.
7. Never force push.
8. Never rewrite Git history.
9. Never commit secrets.
10. Never create meaningless files simply to generate Git activity.
11. Every example must provide genuine educational value.
12. One educational example = one Git commit.
13. Push immediately after each successful commit.
14. If some examples were already created today, create only the remaining amount.
15. Stop immediately once today's total reaches 12.

---

# 3. Repository Structure

Every programming language has its own directory inside `examples/`.

The repository root holds only the top-level sections, so it stays readable:
`examples/`, `interview-prep/`, `coding-challenges/`, `daily-challenges/`,
`resources/` and `scripts/`. Do NOT create a new language folder at the root.

`.gitattributes` keeps GitHub's language bar honest and must not be deleted.
GitHub's Linguist treats a top-level `examples/` directory as documentation and
would otherwise report "Python 100%"; the file opts `examples/` back in and
marks `*.sql` detectable (Linguist types SQL as data, not programming). A new
language added under `examples/` is covered automatically.

Example:

```text
interview-cracker/
│
├── README.md
├── Skill.md
├── TOPICS.md
├── progress.json
│
├── interview-prep/          (see section 3a)
├── coding-challenges/       (see section 3a)
├── daily-challenges/        (see section 3a)
├── resources/               (see section 3a)
├── scripts/
│
└── examples/                the daily example library
    ├── README.md
    │
    ├── python/
    │   ├── basics/
    │   ├── strings/
    │   ├── collections/
    │   ├── algorithms/
    │   ├── data-structures/
    │   ├── files/
    │   └── oop/
    │
    ├── javascript/
    │   ├── basics/
    │   ├── arrays/
    │   ├── objects/
    │   ├── async/
    │   ├── algorithms/
    │   └── utilities/
    │
    ├── typescript/
    │   ├── basics/
    │   ├── interfaces/
    │   ├── generics/
    │   └── utilities/
    │
    ├── java/
    │   ├── basics/
    │   ├── collections/
    │   ├── algorithms/
    │   └── oop/
    │
    ├── c/
    │   ├── basics/
    │   ├── arrays/
    │   ├── pointers/
    │   └── algorithms/
    │
    ├── cpp/
    │   ├── basics/
    │   ├── stl/
    │   ├── algorithms/
    │   └── oop/
    │
    ├── csharp/
    │   ├── basics/
    │   ├── collections/
    │   ├── linq/
    │   └── oop/
    │
    ├── go/
    │   ├── basics/
    │   ├── slices/
    │   ├── maps/
    │   └── concurrency/
    │
    ├── rust/
    │   ├── basics/
    │   ├── ownership/
    │   ├── collections/
    │   └── concurrency/
    │
    ├── sql/
    ├── bash/
    ├── powershell/
    ├── ruby/
    │
    └── (kotlin/ swift/ dart/ php/ r/ ... as they are added)
```

Folders do not need to be created in advance.

Create a language or category directory only when it is actually required.

Do not create empty directories.

---

# 3a. Interview Sections

Alongside the language folders, the repository maintains interview-preparation
material:

```text
examples/             the daily language example library (see section 3)
interview-prep/       question banks with written answers, by subject
coding-challenges/    problems grouped by solving pattern, with tested solutions
daily-challenges/     one dated problem per day, answer in a <details> block
resources/pdf/        PDFs generated from interview-prep/ by scripts/build_pdfs.py
```

Rules for these sections:

1. They are **not** counted toward the daily 12-example target, and are **not**
   registered in `TOPICS.md` or `progress.json`. Those two registries describe
   the language example library only, and `scripts/validate_registry.py`
   enforces that.
2. Every code snippet published in `interview-prep/` or `daily-challenges/`
   must be **executed and verified** before committing. Cross-check against a
   brute-force reference on randomised inputs where one is practical.
3. Every file in `coding-challenges/` must be runnable and self-testing, and
   `python scripts/run_challenges.py` must pass in full before committing.
4. Never state that a question is "asked at" a named company. Those claims are
   not verifiable. Group by subject and difficulty instead.
5. PDFs in `resources/pdf/` are generated artefacts. Edit the Markdown source
   and rerun `python scripts/build_pdfs.py`; never hand-edit a PDF.
6. Commit message prefixes for these sections: `docs(interview-prep):`,
   `feat(coding-challenges):`, `feat(daily-challenges):`, `feat(resources):`.
   The `learn(<language>):` prefix stays reserved for the daily examples.

---

# 4. Language Policy

Any programming language may be used.

Examples include:

- Python
- JavaScript
- TypeScript
- Java
- C
- C++
- C#
- Go
- Rust
- Kotlin
- Swift
- Dart
- Ruby
- PHP
- SQL
- Bash
- PowerShell
- R

Other legitimate programming languages may also be added.

The repository should gradually contain a broad variety of languages.

---

# 5. Daily Language Variety

Do not automatically create all 12 examples in the same language.

Prefer diversity.

Example:

```text
1. Python
2. JavaScript
3. Java
4. SQL
5. Go
6. C++
```

Another day could be:

```text
1. Rust
2. Python
3. TypeScript
4. C#
5. Bash
6. Kotlin
```

Do not use exactly the same language combination every day.

However, language variety must never be prioritized over educational quality.

---

# 6. Difficulty Distribution

For approximately 12 daily examples, prefer:

```text
4 Beginner
6 Intermediate
2 Advanced
```

This is a guideline, not an absolute requirement.

Avoid extremely complex projects.

Most examples should be understandable without requiring an entire application.

---

# 7. No Full-Stack Applications

This repository is NOT intended for large applications.

Do NOT generate:

- Full React applications
- Full Angular applications
- Full Vue applications
- Full backend servers
- Authentication applications
- Complete SaaS projects
- Full-stack applications
- Huge frameworks
- Large boilerplate projects
- Complete mobile applications
- Huge APIs

Examples should normally demonstrate **one focused concept**.

---

# 8. Educational Categories

Examples may cover areas such as:

## Beginner Concepts

- Variables
- Data types
- Conditions
- Loops
- Functions
- Arrays
- Lists
- Strings
- Maps
- Dictionaries
- Sets
- Basic input/output

## Intermediate Concepts

- Recursion
- Searching
- Sorting
- Stack
- Queue
- Linked lists
- Trees
- Graphs
- Hash maps
- File handling
- Error handling
- Regular expressions
- Object-oriented programming

## Practical Programming

- JSON parsing
- CSV processing
- Log parsing
- Date manipulation
- File searching
- Configuration parsing
- Text processing
- Data validation
- CLI utilities
- Environment variables
- File organization
- Duplicate detection

## Algorithms

- Binary search
- Linear search
- Two pointers
- Sliding window
- Breadth-first search
- Depth-first search
- Dynamic programming
- Greedy algorithms
- Backtracking
- Sorting algorithms
- Graph algorithms
- String algorithms

## Language-Specific Concepts

### Python

- List comprehensions
- Generators
- Decorators
- Context managers
- Dataclasses
- Iterators
- Sets
- Collections
- Type hints

### JavaScript

- Closures
- Promises
- async/await
- Array methods
- Object manipulation
- Destructuring
- Higher-order functions
- Modules

### TypeScript

- Interfaces
- Generics
- Utility types
- Type guards
- Enums
- Union types

### Java

- Streams
- Generics
- Collections
- Interfaces
- Classes
- Exceptions
- Records

### C++

- STL
- Templates
- Smart pointers
- Iterators
- Algorithms
- Classes

### Go

- Goroutines
- Channels
- Interfaces
- Maps
- Slices
- Structs

### Rust

- Ownership
- Borrowing
- Lifetimes
- Traits
- Enums
- Pattern matching
- Iterators

### SQL

- Joins
- Aggregation
- CTEs
- Window functions
- Subqueries
- Ranking
- Filtering

---

# 9. File Naming Rules

Every filename must clearly describe what the example teaches.

GOOD:

```text
examples/python/strings/count_word_frequency.py
examples/python/algorithms/find_second_largest_number.py
examples/javascript/arrays/group_objects_by_property.js
examples/java/collections/find_duplicate_elements.java
examples/cpp/algorithms/binary_search_iterative.cpp
examples/go/concurrency/simple_worker_pool.go
examples/rust/ownership/borrow_string_without_move.rs
examples/sql/window-functions/rank_employees_by_salary.sql
```

BAD:

```text
example.py
example1.py
code.py
code2.js
test.java
demo.cpp
today.py
daily.js
program1.c
file6.py
```

Never use meaningless sequential names.

---

# 10. Existing File Protection

Before creating a file, verify that the path does not already exist.

If the file already exists:

```text
DO NOT overwrite it.
```

Instead:

1. Reject the proposed example.
2. Choose another useful topic.
3. Generate a new descriptive filename.
4. Run duplicate detection again.

Existing examples should normally remain untouched.

---

# 11. Strict No-Duplicate Policy

Duplicates are strictly prohibited.

Changing:

- filename
- variable names
- function names
- formatting
- comments
- programming language

does NOT automatically make an example unique.

For example, if the repository already contains:

```text
examples/python/strings/reverse_string.py
```

do not later create:

```text
examples/python/basics/string_reverse.py
```

with essentially the same teaching objective.

Similarly:

```text
examples/python/algorithms/binary_search.py
```

should not be followed by:

```text
examples/python/searching/simple_binary_search.py
```

unless the second example demonstrates a genuinely different concept or technique.

---

# 12. Duplicate Detection Process

Before creating EVERY example, perform duplicate detection.

Check:

1. Existing filenames.
2. Directory names.
3. `TOPICS.md`.
4. `progress.json`.
5. Existing source code.
6. Recent Git history.

Search for important keywords related to the proposed concept.

Example:

```bash
grep -Rni "binary search" .
```

or:

```bash
git grep -i "binary search"
```

Also search related terminology.

Example:

```text
duplicate
duplicates
unique
deduplicate
remove duplicates
```

If a substantially similar example exists:

```text
REJECT THE TOPIC.
```

Choose another topic.

When uncertain, prefer a completely different concept.

---

# 13. TOPICS.md

Maintain a permanent human-readable topic registry:

```text
TOPICS.md
```

Recommended format:

```markdown
# Topics

| Date | Language | Difficulty | Category | Topic | File |
|---|---|---|---|---|---|
| 2026-09-03 | Python | Beginner | Strings | Count word frequency | examples/python/strings/count_word_frequency.py |
| 2026-09-03 | Go | Intermediate | Concurrency | Worker pool using channels | examples/go/concurrency/worker_pool.go |
```

Every example must have one entry.

Never remove historical entries unless correcting an actual error.

---

# 14. progress.json

Maintain a machine-readable registry:

```text
progress.json
```

Example:

```json
{
  "total_examples": 2,
  "examples": [
    {
      "date": "2026-09-03",
      "language": "python",
      "difficulty": "beginner",
      "category": "strings",
      "topic": "Count word frequency",
      "file": "examples/python/strings/count_word_frequency.py"
    },
    {
      "date": "2026-09-03",
      "language": "go",
      "difficulty": "intermediate",
      "category": "concurrency",
      "topic": "Worker pool using channels",
      "file": "examples/go/concurrency/worker_pool.go"
    }
  ]
}
```

The agent MUST inspect this file before choosing new topics.

---

# 15. Daily Resume Protection

The automation may stop unexpectedly because of:

- Internet failure
- GitHub authentication failure
- Computer shutdown
- AI agent crash
- Terminal crash
- Git conflict
- Compiler error
- Network interruption

Therefore NEVER assume that today's count is zero.

At startup:

1. Read `progress.json`.
2. Read `TOPICS.md`.
3. Check Git history.
4. Determine how many examples already exist for today's date.

Then calculate:

```text
remaining = 12 - examples_already_completed_today
```

Rules:

```text
0 completed → create 12
1 completed → create 11
2 completed → create 10
3 completed → create 9
4 completed → create 8
5 completed → create 7
6 completed → create 6
7 completed → create 5
8 completed → create 4
9 completed → create 3
10 completed → create 2
11 completed → create 1
12 completed → create 0 and STOP
```

If today's total is already 12:

```text
STOP IMMEDIATELY.
```

Do not create a thirteenth example.

---

# 16. Startup Procedure

At the beginning of every run:

## Step 1

Enter the repository.

## Step 2

Check repository status.

```bash
git status
```

## Step 3

Do not blindly destroy existing local work.

If unrelated uncommitted user changes exist:

```text
STOP.
```

Report the situation instead of overwriting, resetting, deleting, or committing them.

## Step 4

Synchronize safely.

When the working tree is clean:

```bash
git pull --rebase
```

Never use a destructive reset to resolve normal synchronization problems.

## Step 5

Confirm branch:

```bash
git branch --show-current
```

Normally operate on the repository's default branch.

## Step 6

Inspect recent history:

```bash
git log --oneline -30
```

## Step 7

Read:

```text
TOPICS.md
progress.json
```

## Step 8

Determine today's completed count.

## Step 9

Calculate remaining examples.

---

# 17. Example Quality Requirements

Every example should normally contain:

1. Topic/title.
2. Short explanation.
3. Concepts being demonstrated.
4. Runnable or valid code.
5. Example input when relevant.
6. Example output when relevant.
7. Helpful comments.
8. Complexity explanation when relevant.

Do not over-comment obvious code.

The source itself should remain readable.

---

# 18. Example Python Style

Example:

```python
"""
Topic: Find the second-largest unique number.

Concepts:
- Sets
- Sorting
- List processing

Example:
Input: [4, 8, 2, 8, 6]
Output: 6

Time Complexity:
O(n log n)
"""


def second_largest(numbers):
    unique_numbers = set(numbers)

    if len(unique_numbers) < 2:
        return None

    sorted_numbers = sorted(unique_numbers, reverse=True)

    return sorted_numbers[1]


values = [4, 8, 2, 8, 6]

print(second_largest(values))
```

---

# 19. File Size Guidance

Most examples should contain roughly:

```text
20-120 useful lines
```

This is a guideline rather than a strict requirement.

A simple algorithm may legitimately be shorter.

Do not add meaningless code merely to increase line count.

---

# 20. Code Validation

Before committing, validate the example whenever the required runtime/compiler exists.

## Python

```bash
python examples/<lang>/<category>/example.py
```

or:

```bash
python3 examples/<lang>/<category>/example.py
```

## JavaScript

```bash
node examples/<lang>/<category>/example.js
```

## TypeScript

Use available TypeScript validation tools when configured.

## Go

```bash
go run examples/go/<category>/example.go
```

## Rust

```bash
rustc examples/rust/<category>/example.rs
```

## C

```bash
gcc examples/c/<category>/example.c -o /tmp/example
/tmp/example
```

## C++

```bash
g++ examples/cpp/<category>/example.cpp -o /tmp/example
/tmp/example
```

## Java

Compile/run where Java tooling exists.

## SQL

Validate syntax using available tooling where practical.

If the required compiler/runtime is unavailable, inspect the code carefully.

Do not install large dependencies merely to validate one small example unless specifically authorized.

Never commit code that is known to contain syntax or execution errors.

---

# 21. Temporary Build Files

Compiled binaries and temporary validation files must NOT be committed.

Do not commit files such as:

```text
*.exe
*.class
*.o
*.out
target/
bin/
obj/
__pycache__/
node_modules/
```

Validation artifacts should be created outside the repository where practical.

---

# 22. .gitignore

Maintain an appropriate `.gitignore`.

At minimum consider excluding:

```gitignore
.env
.env.*
*.pem
*.key

__pycache__/
*.pyc

node_modules/

target/

bin/
obj/

*.class
*.o
*.out
*.exe

.DS_Store
Thumbs.db
```

Never remove useful existing `.gitignore` rules without a reason.

---

# 23. Security Rules

Before every commit, check staged changes.

Never commit:

- Passwords
- GitHub tokens
- API keys
- Private keys
- SSH private keys
- `.env` files
- Database credentials
- Authentication tokens
- Cloud credentials
- Personal private information
- Certificates containing secrets

Useful checks include:

```bash
git diff --cached
```

and:

```bash
git status --short
```

If a potential secret is detected:

```text
STOP.
```

Do not commit or push it.

---

# 24. One Example = One Commit

Each educational example must have its own commit.

The commit should contain:

```text
1 new educational source file
+
its TOPICS.md entry
+
its progress.json entry
```

Do not create all 12 code examples and combine them into one commit.

---

# 25. Commit Workflow

For each example:

## Step 1 — Generate

Create exactly one educational example.

## Step 2 — Validate

Run or compile it when practical.

## Step 3 — Register

Update:

```text
TOPICS.md
progress.json
```

## Step 4 — Inspect

```bash
git status --short
```

Then:

```bash
git diff
```

## Step 5 — Stage only intended files

Example:

```bash
git add examples/python/strings/count_word_frequency.py TOPICS.md progress.json
```

Do NOT blindly use:

```bash
git add .
```

when unrelated changes may exist.

## Step 6 — Inspect staged changes

```bash
git diff --cached
```

## Step 7 — Commit

Use:

```text
learn(<language>): <specific topic>
```

Examples:

```text
learn(python): count word frequencies with dictionary
```

```text
learn(javascript): group objects by property
```

```text
learn(java): demonstrate queue using array deque
```

```text
learn(go): implement worker pool with channels
```

```text
learn(sql): rank employees using window functions
```

BAD commit messages:

```text
update
commit
daily
day 1
activity
green
github activity
file 3
another commit
```

---

# 26. Push Rule

Immediately after every successful commit:

```bash
git push
```

Do not move to the next example until the push succeeds.

Workflow:

```text
CREATE
↓
VALIDATE
↓
REGISTER
↓
REVIEW
↓
COMMIT
↓
PUSH
↓
VERIFY
↓
NEXT EXAMPLE
```

---

# 27. Push Failure

If `git push` fails:

1. Stop creating new examples.
2. Read the Git error.
3. Diagnose the problem.
4. Resolve it safely if possible.
5. Retry the push.
6. Continue only after the existing commit has been pushed successfully.

Never solve normal errors with:

```bash
git push --force
```

or:

```bash
git push -f
```

Force pushing is prohibited unless the repository owner explicitly requests it for a specific situation.

---

# 28. Network Failure Protection

If a commit succeeds locally but push fails because of network problems:

```text
DO NOT create another commit.
```

First push the existing commit successfully.

This keeps the intended relationship:

```text
1 example
=
1 commit
=
1 successful push
```

---

# 29. Daily Workflow

The intended daily process is:

```text
START

↓
Sync repository safely

↓
Read TOPICS.md

↓
Read progress.json

↓
Count today's completed examples

↓
Calculate remaining examples

↓
Choose unique topic #1

↓
Duplicate check

↓
Create example

↓
Validate

↓
Update registries

↓
Commit

↓
Push

↓
Choose unique topic #2

↓
Repeat

...

↓
Reach 12 total examples for today

↓
Final verification

↓
STOP
```

---

# 30. Topic Selection Strategy

Prefer examples that developers may actually search for or want to understand.

GOOD topics:

```text
Count word frequency
Find second largest number
Merge overlapping intervals
Validate balanced parentheses
Parse CSV without duplicate records
Find duplicate files using hashes
Implement LRU cache
Flatten nested arrays
Group objects by property
Retry function with exponential backoff
Read large file line by line
Detect cycle in linked list
Find missing number
Merge two sorted arrays
Implement rate limiter concept
Calculate moving average
Traverse directory recursively
Find longest substring without repeating characters
Use SQL ROW_NUMBER
Use SQL running totals
Process logs by severity
Build worker pool with Go channels
Demonstrate Rust borrowing
```

Avoid trivial variations of existing topics.

---

# 31. Progressive Learning Strategy

Over time, the repository should become more valuable.

Do not endlessly create basic examples such as:

```text
add two numbers
subtract numbers
multiply numbers
print hello world
```

Gradually move through:

```text
Basics
↓
Collections
↓
Problem solving
↓
Algorithms
↓
Data structures
↓
Language features
↓
Practical utilities
↓
Advanced concepts
```

Maintain a healthy mixture so beginners can still use the repository.

---

# 32. Cross-Language Examples

A concept MAY occasionally exist in multiple languages if the educational objective specifically includes showing the language-specific implementation.

For example:

```text
examples/python/algorithms/binary_search.py
examples/rust/algorithms/binary_search.rs
```

may be acceptable if both genuinely demonstrate language-specific techniques.

However:

Do NOT automatically translate every program into ten languages.

Cross-language repetition should be intentional and educational, not a method of producing easy commits.

---

# 33. README Purpose

`README.md` should describe the project as an educational resource.

Suggested description:

```markdown
# Daily Code Learning

A growing collection of focused programming examples designed to help
developers understand one concept at a time.

The repository contains examples across multiple programming languages,
covering algorithms, data structures, language features, practical utilities,
and problem-solving techniques.

Each example is intentionally small enough to study independently.

Explore the language folders to start learning.
```

Do not describe the repository as:

```text
A repository for making my GitHub contribution graph green.
```

Its public purpose should genuinely be education.

---

# 34. README Statistics

The README may contain statistics such as:

```text
Examples: 328
Languages: 14
Categories: 40+
```

Do not modify README statistics after every individual example.

If updating statistics automatically, do so once after the twelfth daily example.

README changes should not require an additional meaningless seventh commit.

Include the daily README update with the twelfth example's commit when appropriate.

---

# 35. Do Not Create Artificial Contributions

Never:

- Create empty commits.
- Create random files.
- Create files containing only timestamps.
- Rename files solely for another commit.
- Delete and recreate files.
- Make whitespace-only changes for activity.
- Change comments solely to create commits.
- Generate meaningless documentation updates.
- Backdate commits.
- Change author dates for contribution manipulation.

Every commit must represent genuine repository improvement.

---

# 36. Idempotency

The agent must be safe to execute multiple times during the same day.

Running the agent again must NOT automatically create another 12 examples.

Every execution must first determine the current daily state.

Example:

Morning execution:

```text
Created: 12
```

Evening execution:

```text
Existing today: 12
Remaining: 0
Action: STOP
```

Not:

```text
Create another 12
```

---

# 37. Date Handling

Use the local system date for the repository's daily tracking.

Determine it programmatically where possible.

Examples:

Linux/macOS:

```bash
date +%F
```

PowerShell:

```powershell
Get-Date -Format "yyyy-MM-dd"
```

Store dates in:

```text
YYYY-MM-DD
```

Example:

```text
2026-09-03
```

Never manually assume today's date if the system can provide it.

---

# 38. Concurrency Protection

Only one instance of this automation should modify the repository at a time.

Before starting, check whether another instance appears to be actively working.

If a lock mechanism exists, use it.

Never allow two agents to independently calculate:

```text
0 examples today
```

and both create 12.

That could produce 24 examples.

---

# 39. User Work Protection

The repository may occasionally contain manual changes created by the owner.

Never automatically:

```bash
git reset --hard
```

Never automatically:

```bash
git clean -fd
```

Never automatically delete untracked user files.

Never automatically discard local modifications.

If unexpected changes are present:

```text
STOP AND REPORT THEM.
```

Protecting user work is more important than completing the daily target.

---

# 40. Repository Health

Periodically ensure the repository remains easy to browse.

Avoid:

- Thousands of files in one directory.
- Meaningless nesting.
- Duplicate category folders.
- Slightly different category names.

For example, do not create all three:

```text
examples/python/algorithm/
examples/python/algorithms/
examples/python/algo/
```

Use one canonical directory:

```text
examples/python/algorithms/
```

---

# 41. Category Naming

Prefer lowercase kebab-case directory names.

GOOD:

```text
data-structures
file-handling
dynamic-programming
window-functions
error-handling
```

Avoid:

```text
DataStructures
data_structures
Data Structures
ds
```

unless an established repository convention already exists.

Respect existing conventions instead of continuously reorganizing the repository.

---

# 42. Quality Gate

Before EVERY commit, answer all of these:

```text
[ ] Is this topic educational?
[ ] Is it genuinely different from existing examples?
[ ] Did I search TOPICS.md?
[ ] Did I search progress.json?
[ ] Did I search existing source code?
[ ] Is the filename descriptive?
[ ] Is it in the correct language folder?
[ ] Is the category appropriate?
[ ] Does the example work?
[ ] Did I validate it where possible?
[ ] Is the code readable?
[ ] Are comments helpful rather than excessive?
[ ] Did I update TOPICS.md?
[ ] Did I update progress.json?
[ ] Are only intended files staged?
[ ] Are there no credentials or secrets?
[ ] Is the commit message descriptive?
```

If any important item fails:

```text
DO NOT COMMIT.
```

Fix it first.

---

# 43. Daily Limit Verification

Before creating each new example:

Recalculate today's total from the repository state.

Do not rely exclusively on an in-memory counter.

This prevents accidental overproduction after interruptions or partial restarts.

If today's count reaches 12:

```text
STOP.
```

---

# 44. Final Daily Verification

After the twelfth successful push:

Run:

```bash
git status
```

The working tree should normally be clean.

Then inspect today's history:

```bash
git log --since="today 00:00" --oneline
```

Also verify `progress.json`.

Confirm:

```text
Today's educational examples = 12
```

Do not create another commit merely to report completion.

---

# 45. Final Daily Report

After successful completion, output a report similar to:

```text
DAILY CODE LEARNING COMPLETE

Date: 2026-09-03

Target: 12
Completed today: 12
Remaining: 0

Examples:

1. Python
   Topic: Count word frequency
   File: examples/python/strings/count_word_frequency.py
   Validation: Passed

2. JavaScript
   Topic: Group objects by property
   File: examples/javascript/arrays/group_objects_by_property.js
   Validation: Passed

3. Java
   Topic: Queue using ArrayDeque
   File: examples/java/collections/queue_using_array_deque.java
   Validation: Passed

4. SQL
   Topic: Rank employees with ROW_NUMBER
   File: examples/sql/window-functions/rank_employees.sql
   Validation: Checked

5. Go
   Topic: Worker pool using channels
   File: examples/go/concurrency/worker_pool.go
   Validation: Passed

6. C++
   Topic: Merge overlapping intervals
   File: examples/cpp/algorithms/merge_overlapping_intervals.cpp
   Validation: Passed

Commits created: 12
Successful pushes: 12
Duplicate proposals rejected: 2
Validation issues corrected: 1

Repository status: Clean
Daily target reached: YES
```

---

# 46. Failure Report

If the daily target cannot be completed, do not falsely report success.

Example:

```text
DAILY CODE LEARNING PARTIALLY COMPLETE

Date: 2026-09-03

Completed: 8 / 12
Remaining: 4

Stopped because:
Git push authentication failed.

Last successful example:
examples/javascript/arrays/group_objects_by_property.js

No additional commits were created after the push failure.

Action required:
Restore GitHub authentication and rerun the agent.

The agent should resume from 8 / 12.
```

---

# 47. Priority Order

When rules conflict, use this priority:

```text
1. Protect user files
2. Protect secrets/security
3. Protect Git history
4. Avoid duplicate content
5. Ensure code correctness
6. Ensure educational value
7. Preserve repository organization
8. Reach daily target
9. Maintain language variety
```

Reaching 12 examples is NEVER more important than repository safety or quality.

---

# 48. Autonomous Decision Permission

The agent is authorized to independently decide:

- Today's programming languages.
- Example topics.
- Difficulty levels.
- Categories.
- Descriptive filenames.
- Appropriate small implementations.
- Appropriate validation commands.

The agent does NOT need to ask the user to select topics every day.

However, all decisions must comply with this skill.

---

# 49. Do Not Ask Unnecessary Questions

If the repository is correctly configured and no safety issue exists, proceed automatically.

Do not ask:

```text
Should I create Python today?
Should I create example #2?
Should I push this commit?
Should I continue?
```

The purpose of this skill is autonomous daily maintenance.

Stop and request user intervention only when genuinely necessary, such as:

- Authentication failure.
- Merge conflict requiring judgment.
- Unexpected user modifications.
- Potential secret exposure.
- Repository corruption.
- Missing Git remote.
- Permission failure.

---

# 50. Definition of Success

A successful day is NOT:

```text
12 random commits.
```

A successful day is:

```text
12 unique
+
useful
+
educational
+
organized
+
validated
+
properly documented
+
individually committed
+
successfully pushed

programming examples.
```

After the twelfth successful example and push:

```text
STOP FOR THE DAY.
```