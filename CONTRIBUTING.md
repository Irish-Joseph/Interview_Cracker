# Contributing

Thanks for helping improve Daily Code Learning. Contributions should teach one
clear concept through a small, focused example.

## Add an example

1. Check `TOPICS.md` and `progress.json` to avoid duplicating an existing topic.
2. Put the example in the matching language and category directory.
3. Include comments that explain the important idea and expected output.
4. Run the example with the appropriate compiler or interpreter when available.
5. Add matching entries to `TOPICS.md` and `progress.json` and update the totals
   in `README.md` and `progress.json`.
6. Keep one educational example in one commit.

## Open a pull request

- Create a descriptive branch such as `learn/python-binary-search`.
- Use a focused commit message, for example
  `learn(python): demonstrate binary search insertion points`.
- Explain what the example teaches and include the validation command and result
  in the pull-request description.
- Keep unrelated changes in separate pull requests so each change is easy to
  review and revert.

## Quality checklist

- The topic is new to this repository.
- The example is useful and has no secrets or generated build artifacts.
- File paths and topic names match in both registries.
- The code handles its demonstrated edge cases.
- The pull request targets the default `main` branch.

For the repository's complete maintenance rules, see `Skill.md`.

## Collaborating on a change

When two or more people genuinely work on the same change, record each person's
contribution with Git's `Co-authored-by` trailer. The email in the trailer must
belong to that contributor's GitHub account. Do not add a co-author who did not
participate in the change.

Questions about the examples belong in the repository's
[Q&A Discussions](https://github.com/Irish-Joseph/code-by-example/discussions/categories/q-a),
where the question author can mark a helpful response as the accepted answer.
