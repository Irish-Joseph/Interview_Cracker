"""
Topic: Path operations with pathlib.

Concepts:
- PurePath vs Path (string parsing vs filesystem interaction)
- Building paths with / instead of os.path.join
- .parent, .name, .suffix, .with_suffix
- .glob for pattern matching, .relative_to / .resolve
- Checking existence without try/except

Example:
Input:  repo_root / "examples" / "python" / "json" / "data.json"
name: data.json   parent ends with: json
suffix: .json   with_suffix: data.csv
glob finds: one or more .py files under examples/python

Time Complexity: O(1) for pure path math; glob/resolve touch the disk.
"""

from pathlib import Path, PurePosixPath

# Pure paths: no filesystem access, just string-level manipulation.
p = PurePosixPath("/home/user/projects/app/src/main.py")
print("name:", p.name)                 # main.py
print("stem:", p.stem)                 # main
print("suffix:", p.suffix)             # .py
print("parent:", p.parent)             # /home/user/projects/app/src
print("with_suffix:", p.with_suffix(".rs"))  # /home/user/.../main.rs
print("is_absolute:", p.is_absolute())

# Real paths: the / operator builds paths (no more os.path.join).
root = Path("examples") / "python"
target = root / "json" / "data.json"
print("built:", target.as_posix())
print("depth parts:", len(target.parts))   # examples, python, json, data.json

# relative_to raises ValueError if the prefix doesn't match —
# a convenient way to assert path relationships.
base = Path("a/b/c.txt")
print("relative:", base.relative_to("a/b"))     # c.txt

# Filesystem operations from the repository root:
if root.exists():
    found = list(root.glob("**/*.py"))
    print("py files under examples/python:", len(found))
    print("first one:", found[0].as_posix())
else:
    print("(run from the repository root for the filesystem part)")
