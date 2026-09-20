"""
Topic: JSON parsing and serialization with the json module.

Concepts:
- json.loads / json.dumps (strings) vs json.load / json.dump (files)
- Default object (dict, list) to JSON type mapping
- Handling data JSON cannot represent (sets, datetime, tuples)
- Common parsing pitfalls: duplicate keys, indentation, ensure_ascii

Example:
Input:  {"name": "Ada", "tags": ["math", "code"], "score": 42}
Round-trips back to: {'name': 'Ada', 'tags': ['math', 'code'], 'score': 42}
"""

import json
import os
import tempfile
from datetime import date

# JSON text -> Python objects. Valid JSON requires double quotes.
text = '{"name": "Ada", "tags": ["math", "code"], "score": 42}'
data = json.loads(text)
print("parsed:", data)
print("type of tags:", type(data["tags"]).__name__)  # lists become lists

# Python objects -> JSON text. sort_keys + indent make output stable.
print(
    "serialized:",
    json.dumps(data, sort_keys=True, indent=2).replace("\n", " "),
)

# Tuples, sets and datetimes are NOT valid JSON — encode them yourself.
def default(o):
    if isinstance(o, date):
        return o.isoformat()
    if isinstance(o, set):
        return sorted(o)
    raise TypeError(f"cannot serialize {type(o).__name__}")

payload = {
    "day": date(2026, 9, 19),
    "likes": {"tea", "coffee"},
    "point": (3, 4),
}
print("with default:", json.dumps(payload, default=default))

# Loading from a file handle instead of a string:
import tempfile, os

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                 encoding="utf-8") as fh:
    json.dump(data, fh)
    path = fh.name

with open(path, encoding="utf-8") as fh:
    from_file = json.load(fh)
os.unlink(path)
print("round trip through file:", from_file == data)

# Pitfall: duplicate keys — the LAST one wins, without any warning.
print("duplicates:", json.loads('{"a": 1, "a": 2}'))
