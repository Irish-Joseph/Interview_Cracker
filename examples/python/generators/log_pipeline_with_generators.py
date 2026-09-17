"""
Topic: Composing generator functions into a lazy log-processing pipeline.

Concepts:
- Generator functions (`yield`) and lazy evaluation
- Producer/consumer pipeline composition
- Memory-constant streaming of large files
- Parsing with str methods (no regex needed)
- Early termination via StopIteration

Instead of building one giant list of all log lines in memory, each
stage is a generator that pulls one item at a time. Data flows
through the whole chain one record at a time:

    lines -> parse -> filter -> summarize

Memory usage is O(1) in the file size (plus O(1) per stage), which
makes this pattern the standard way to process files bigger than RAM.

Example input line:
    2026-09-05T12:00:01Z INFO  auth   user=42 login ok
    2026-09-05T12:00:02Z ERROR db     user=42 timeout after 30s

Time Complexity: O(total lines) — each line touches each stage once
"""

import re
from collections import Counter
from typing import Iterator


def read_lines(path: str) -> Iterator[str]:
    """Stage 1: yield raw lines one at a time (never loads the file)."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            yield line.rstrip("\n")


LINE_RE = re.compile(
    r"^(?P<timestamp>\S+)\s+(?P<level>\w+)\s+(?P<service>\w+)\s+(?P<message>.*)$"
)


def parse_lines(lines: Iterator[str]) -> Iterator[dict]:
    """Stage 2: turn raw text into structured dicts; skip malformed."""
    for line in lines:
        match = LINE_RE.match(line)
        if match:
            yield match.groupdict()


def only_errors(records: Iterator[dict]) -> Iterator[dict]:
    """Stage 3: pass through only ERROR/CRITICAL records."""
    for record in records:
        if record["level"] in ("ERROR", "CRITICAL"):
            yield record


def summarize_by_service(records: Iterator[dict]) -> dict[str, int]:
    """Stage 4 (terminal): consume the stream, build a small summary.

    Only this final structure lives in memory — the individual
    records never accumulate.
    """
    counts: Counter[str] = Counter()
    for record in records:
        counts[record["service"]] += 1
    return dict(counts)


# --- Demo -----------------------------------------------------------------

SAMPLE_LOG = """\
2026-09-05T12:00:01Z INFO  auth   user=42 login ok
2026-09-05T12:00:02Z ERROR db     user=42 timeout after 30s
2026-09-05T12:00:03Z WARN  auth   user=7 slow response
2026-09-05T12:00:04Z ERROR db     user=9 connection refused
2026-09-05T12:00:05Z INFO  api    healthcheck ok
2026-09-05T12:00:06Z CRITICAL db  user=1 disk full
this line is malformed and gets skipped
2026-09-05T12:00:07Z ERROR api    user=3 upstream 502
"""


def pipeline_from_text(text: str) -> dict[str, int]:
    """Run the same pipeline over in-memory text (for the demo)."""
    lines = (line for line in text.splitlines())   # generator, not a list
    parsed = parse_lines(lines)
    errors = only_errors(parsed)
    return summarize_by_service(errors)


summary = pipeline_from_text(SAMPLE_LOG)
print("errors by service:", summary)
# -> {'db': 3, 'api': 1}

# --- Early termination: generators stop the world -------------------------
# A consumer can stop partway and every upstream generator stops too.

def first_n(iterable: Iterator, n: int) -> list:
    return [item for _, item in zip(range(n), iterable)]


count_stream = (r["level"] for r in parse_lines(
    line for line in SAMPLE_LOG.splitlines()))

print("first 3 levels:", first_n(count_stream, 3))
# -> ['INFO', 'ERROR', 'WARN']
# The remaining lines are never parsed at all.

# --- The same pipeline on a real file -------------------------------------
# def main():
#     with open("app.log", "w", encoding="utf-8") as fh:
#         fh.write(SAMPLE_LOG)
#     result = summarize_by_service(
#         only_errors(parse_lines(read_lines("app.log")))
#     )
#     print(result)   # same {'db': 3, 'api': 1}, any file size
