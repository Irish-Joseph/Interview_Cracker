"""Validate the example registry and the summary shown in README.md."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = {"date", "language", "difficulty", "category", "topic", "file"}


def read_summary(readme: str, label: str) -> int:
    match = re.search(rf"^{re.escape(label)}:\s*(\d+)\s*$", readme, re.MULTILINE)
    if not match:
        raise ValueError(f"README.md has no '{label}: <number>' summary")
    return int(match.group(1))


def main() -> int:
    errors: list[str] = []
    registry = json.loads((ROOT / "progress.json").read_text(encoding="utf-8"))
    examples = registry.get("examples", [])

    if registry.get("total_examples") != len(examples):
        errors.append("progress.json total_examples does not match its example count")

    paths: list[str] = []
    for index, example in enumerate(examples, start=1):
        missing = REQUIRED_FIELDS - example.keys()
        if missing:
            errors.append(f"registry item {index} is missing: {', '.join(sorted(missing))}")
            continue
        path = example["file"]
        paths.append(path)
        if not (ROOT / path).is_file():
            errors.append(f"registered file does not exist: {path}")

    duplicates = [path for path, count in Counter(paths).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate registry paths: {', '.join(sorted(duplicates))}")

    topic_paths = {
        line.rsplit("|", 2)[1].strip()
        for line in (ROOT / "TOPICS.md").read_text(encoding="utf-8").splitlines()
        if re.match(r"^\| \d{4}-\d{2}-\d{2} \|", line)
    }
    registry_paths = set(paths)
    if topic_paths != registry_paths:
        missing_from_topics = registry_paths - topic_paths
        missing_from_registry = topic_paths - registry_paths
        if missing_from_topics:
            errors.append("missing from TOPICS.md: " + ", ".join(sorted(missing_from_topics)))
        if missing_from_registry:
            errors.append("missing from progress.json: " + ", ".join(sorted(missing_from_registry)))

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    expected = {
        "Examples": len(examples),
        "Languages": len({example["language"] for example in examples}),
        "Categories": len({(example["language"], example["category"]) for example in examples}),
    }
    for label, value in expected.items():
        try:
            actual = read_summary(readme, label)
        except ValueError as error:
            errors.append(str(error))
        else:
            if actual != value:
                errors.append(f"README.md {label} is {actual}; expected {value}")

    if errors:
        print("Registry validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(examples)} examples across {expected['Languages']} languages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
