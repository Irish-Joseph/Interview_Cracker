"""Run every coding challenge's self-tests and report the results."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHALLENGES = ROOT / "coding-challenges"


def main() -> int:
    files = sorted(CHALLENGES.rglob("*.py"))
    if not files:
        print("No challenge files found.", file=sys.stderr)
        return 1

    failures: list[tuple[Path, str]] = []
    for path in files:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        relative = path.relative_to(ROOT).as_posix()
        if result.returncode == 0:
            print(f"PASS  {relative}")
        else:
            print(f"FAIL  {relative}")
            failures.append((path, (result.stderr or result.stdout).strip()))

    print()
    print(f"{len(files) - len(failures)}/{len(files)} challenges passed.")

    for path, error in failures:
        print(f"\n--- {path.relative_to(ROOT).as_posix()} ---\n{error}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
