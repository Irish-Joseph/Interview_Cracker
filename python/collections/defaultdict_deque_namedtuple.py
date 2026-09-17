"""
Topic: Beyond dict and list - defaultdict, deque, namedtuple and ChainMap.

The `collections` module ships four containers that replace a lot of
hand-written boilerplate:

- defaultdict  - a dict that builds a missing value instead of raising KeyError
- deque        - a list-like sequence with O(1) appends/pops at BOTH ends
- namedtuple   - a tuple whose fields also have names
- ChainMap     - several mappings searched in order, without copying them

Concepts:
- Grouping without `setdefault` / `if key not in d`
- Why `list.pop(0)` is O(n) but `deque.popleft()` is O(1)
- Lightweight records that stay tuples (unpackable, hashable, immutable)
- Layered configuration lookup

Example output is printed at the bottom of the file.
"""

from collections import ChainMap, Counter, defaultdict, deque, namedtuple

# ---------------------------------------------------------------------------
# 1. defaultdict - grouping
# ---------------------------------------------------------------------------

WORDS = ["apple", "avocado", "banana", "blueberry", "apricot", "cherry"]


def group_by_first_letter(words):
    """Group words by their first letter.

    The factory (here `list`) is called with no arguments whenever a key is
    read for the first time, so `groups[letter].append(...)` always works.
    """
    groups = defaultdict(list)
    for word in words:
        groups[word[0]].append(word)
    return dict(groups)  # convert back so printing shows a plain dict


def count_lengths(words):
    """defaultdict(int) starts every missing counter at 0."""
    lengths = defaultdict(int)
    for word in words:
        lengths[len(word)] += 1
    return dict(sorted(lengths.items()))


# ---------------------------------------------------------------------------
# 2. deque - a queue that is fast at both ends
# ---------------------------------------------------------------------------


def run_task_queue(tasks):
    """FIFO processing: append on the right, pop from the left.

    A list would work, but `list.pop(0)` shifts every remaining element
    (O(n) per pop). `deque.popleft()` is O(1).
    """
    queue = deque(tasks)
    order = []
    while queue:
        task = queue.popleft()
        order.append(task)
        if task == "deploy":
            # Urgent follow-up work jumps the queue.
            queue.appendleft("smoke-test")
    return order


def last_n_lines(lines, n):
    """maxlen turns a deque into a fixed-size sliding window.

    Older items are dropped automatically, so memory stays constant even
    when `lines` is a huge stream.
    """
    window = deque(maxlen=n)
    for line in lines:
        window.append(line)
    return list(window)


# ---------------------------------------------------------------------------
# 3. namedtuple - a record that is still a tuple
# ---------------------------------------------------------------------------

Point = namedtuple("Point", ["x", "y"])


def namedtuple_demo():
    origin = Point(0, 0)
    target = Point(x=3, y=4)

    x, y = target                      # still unpacks like a tuple
    distance = ((x - origin.x) ** 2 + (y - origin.y) ** 2) ** 0.5

    # Immutable: `_replace` returns a new instance instead of mutating.
    shifted = target._replace(y=10)

    return {
        "target": target,
        "fields": target._fields,
        "as_dict": target._asdict(),
        "distance": distance,
        "shifted": shifted,
        "hashable": {origin, target, shifted} != set(),
    }


# ---------------------------------------------------------------------------
# 4. ChainMap - layered lookup without merging
# ---------------------------------------------------------------------------

DEFAULTS = {"host": "localhost", "port": 8080, "debug": False}
CONFIG_FILE = {"port": 9000}
CLI_FLAGS = {"debug": True}


def resolve_settings():
    """First mapping wins; the originals are never copied or mutated."""
    settings = ChainMap(CLI_FLAGS, CONFIG_FILE, DEFAULTS)
    return dict(settings), settings["port"], settings["debug"]


# ---------------------------------------------------------------------------
# 5. Counter arithmetic (the part people miss)
# ---------------------------------------------------------------------------


def counter_arithmetic():
    """Counters support most_common() plus +, -, & and | between counters."""
    monday = Counter(["tea", "coffee", "tea", "water"])
    tuesday = Counter(["coffee", "coffee", "juice"])
    return {
        "top_monday": monday.most_common(1),
        "combined": dict(monday + tuesday),
        "only_extra_on_tuesday": dict(tuesday - monday),
        "shared_minimums": dict(monday & tuesday),
    }


if __name__ == "__main__":
    print("grouped:", group_by_first_letter(WORDS))
    print("length counts:", count_lengths(WORDS))

    print("queue order:", run_task_queue(["build", "test", "deploy", "notify"]))
    print("last 3 lines:", last_n_lines([f"line-{i}" for i in range(1, 9)], 3))

    for key, value in namedtuple_demo().items():
        print(f"{key}: {value}")

    merged, port, debug = resolve_settings()
    print("settings:", merged)
    print(f"port={port} debug={debug}")

    for key, value in counter_arithmetic().items():
        print(f"{key}: {value}")

# Expected output:
# grouped: {'a': ['apple', 'avocado', 'apricot'], 'b': ['banana', 'blueberry'],
#           'c': ['cherry']}
# length counts: {5: 1, 6: 2, 7: 2, 9: 1}
# queue order: ['build', 'test', 'deploy', 'smoke-test', 'notify']
# last 3 lines: ['line-6', 'line-7', 'line-8']
# ...
# settings: {'host': 'localhost', 'port': 9000, 'debug': True}
