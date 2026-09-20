# Contributing

Thanks for helping improve Interview Cracker. Everything here should teach one
clear idea, and be correct.

The repository has four contributable areas, each with its own checklist below.

---

## Adding a language example (`examples/`)

1. Check `TOPICS.md` and `progress.json` to avoid duplicating an existing topic.
2. Put the example at `examples/<language>/<category>/<descriptive_name>.<ext>`.
   Language folders live inside `examples/`, never at the repository root.
3. Include comments explaining the important idea and the expected output.
4. Run the example with the appropriate compiler or interpreter when available.
   If no toolchain exists on your machine, review it carefully and note
   `validated by inspection` in the file header.
5. Add matching entries to `TOPICS.md` and `progress.json` (paths there are
   relative to the repository root, so they start with `examples/`).
6. Keep one example to one commit, prefixed `learn(<language>):`.

`python scripts/validate_registry.py` must pass.

---

## Adding an interview question (`interview-prep/`)

1. Follow the existing shape: `### 🟢/🟡/🔴 Q.` heading, then `**Answer.**` with
   the direct answer first, then the reasoning.
2. **Run every code snippet you publish.** A wrong answer in a revision guide is
   worse than no answer.
3. Prefer explaining the trade-off over stating a rule.
4. Do not claim a question is "asked at" any named company — those claims are
   not verifiable, and preparing for a rumoured list is worse practice than
   understanding the topic.
5. Add the file to the table in `interview-prep/README.md`.
6. Commit prefix: `docs(interview-prep):`.

If you change the Markdown, regenerate the PDFs (see below) in the same PR.

---

## Adding a coding challenge (`coding-challenges/`)

1. Put it in the folder for the **pattern** that solves it, not the data
   structure it happens to use.
2. Use the existing file shape: a docstring with PROBLEM / EXAMPLES /
   CONSTRAINTS / HINT / COMPLEXITY, then the solution, then `_tests()`.
3. The hint must point at the insight **without** giving the code.
4. Tests must cover the empty input, the single element, and the case that
   breaks the naive approach. Cross-check against a brute-force reference on
   randomised inputs wherever that is practical.
5. Add a row to the pattern's `README.md` table.
6. Commit prefix: `feat(coding-challenges):`.

`python scripts/run_challenges.py` must pass in full.

---

## Adding a daily challenge (`daily-challenges/`)

1. Copy `daily-challenges/TEMPLATE.md` to `YYYY/MM/YYYY-MM-DD.md`.
2. Keep the hint and the solution inside `<details>` blocks so the problem can be
   read without spoilers.
3. Run the solution before publishing it, and state the complexity honestly.
4. Include the "common wrong answer" section — it is often the most useful part.
5. Add a row to the index in `daily-challenges/README.md`.
6. Commit prefix: `feat(daily-challenges):`.

---

## Regenerating the site and PDFs

Both are **generated**. Edit the Markdown, never the output.

```bash
pip install markdown pymdown-extensions pygments jinja2 pillow reportlab

python scripts/build_site.py            # docs/ - the GitHub Pages site
python scripts/build_social_preview.py  # docs/assets/social-preview.png
python scripts/build_pdfs.py            # resources/pdf/
```

`build_site.py` deletes and recreates `docs/`, so anything that must live at
the site root (the Search Console file, `CNAME`, `robots.txt`) is written *by
the script*. Adding such a file by hand will lose it on the next build.

Commit prefix: `chore(site):`.

---

## Opening a pull request

- Branch descriptively: `learn/python-binary-search`, `prep/add-graph-questions`.
- Add a new language under `examples/`, and add it to the table in
  `examples/README.md`.
- Say what the change teaches, and include the validation command **and its
  output** in the description.
- Keep unrelated changes in separate pull requests.
- Target the default `main` branch.

## Quality checklist

- The topic is new to this repository.
- Code has been executed, not just read — or is explicitly marked otherwise.
- Complexity claims are correct.
- No secrets, no generated build artefacts.
- File paths and topic names match across both registries.
- Edge cases are handled and tested.

For the repository's complete maintenance rules, see `Skill.md`.

## Collaborating on a change

When two or more people genuinely work on the same change, record each person's
contribution with Git's `Co-authored-by` trailer. The email in the trailer must
belong to that contributor's GitHub account. Do not add a co-author who did not
participate in the change.

Questions belong in
[Q&A Discussions](https://github.com/Irish-Joseph/Interview_Cracker/discussions/categories/q-a),
where the question author can mark a helpful response as the accepted answer.
