# Examples

126 focused, runnable programs across 13 languages. **One concept per
file** — each is small enough to read in a sitting, and most print their own
expected output.

These are the learning half of the repository. For interview preparation, see
[`interview-prep/`](../interview-prep/) and
[`coding-challenges/`](../coding-challenges/).

## How the files are organised

```
examples/<language>/<category>/<descriptive_name>.<ext>
```

So `examples/python/algorithms/binary_search_iterative.py` is a Python example,
in the algorithms category, about iterative binary search. Filenames describe
what they teach — there are no `example1.py` files here.

Every file opens with a header stating the topic, the concepts it demonstrates,
and its expected output, so you can tell whether it is what you want without
running it.

## Languages

| Language | Examples | Categories |
|---|---|---|
| [Python](python/) | 17 | `algorithms`, `basics`, `collections`, `context-managers`, `data-models`, `dates`, `decorators`, `files`, `generators`, `oop`, `standard-library`, `strings` |
| [SQL](sql/) | 12 | `aggregation`, `filters`, `joins`, `recursive-ctes`, `subqueries`, `transactions`, `window-functions` |
| [Go](go/) | 11 | `algorithms`, `concurrency`, `data-structures`, `errors`, `files`, `generics`, `interfaces`, `maps`, `slices` |
| [JavaScript](javascript/) | 11 | `arrays`, `async`, `basics`, `collections`, `generators`, `objects`, `utilities` |
| [Rust](rust/) | 11 | `basics`, `closures`, `concurrency`, `enums`, `error-handling`, `iterators`, `lifetimes`, `options`, `ownership`, `strings`, `traits` |
| [Bash](bash/) | 10 | `arrays`, `basics`, `scripting`, `testing`, `utilities` |
| [C](c/) | 10 | `arrays`, `basics`, `data-structures`, `files`, `pointers`, `strings` |
| [Java](java/) | 10 | `algorithms`, `collections`, `exceptions`, `generics`, `oop`, `optional`, `records`, `streams`, `strings` |
| [TypeScript](typescript/) | 10 | `advanced-types`, `async`, `basics`, `enums`, `generics`, `interfaces`, `narrowing`, `unions`, `utility-types` |
| [C++](cpp/) | 9 | `algorithms`, `data-structures`, `error-handling`, `operators`, `raii`, `smart-pointers`, `stl`, `sum-types`, `templates` |
| [C#](csharp/) | 9 | `async`, `basics`, `collections`, `delegates`, `error-handling`, `linq`, `methods`, `patterns` |
| [Ruby](ruby/) | 4 | `basics`, `blocks`, `pattern-matching` |
| [PowerShell](powershell/) | 2 | `error-handling`, `objects` |

## Running them

Most examples are self-contained with no dependencies:

```bash
python examples/python/collections/defaultdict_deque_namedtuple.py
node    examples/javascript/generators/generators_and_iterators.js
bash    examples/bash/arrays/indexed_and_associative_arrays.sh
```

Compiled languages need the usual toolchain:

```bash
gcc -Wall examples/c/files/read_write_text_file.c -o demo && ./demo
g++ -std=c++20 examples/cpp/operators/operator_overloading.cpp -o demo && ./demo
go  run examples/go/generics/type_parameters_and_constraints.go
rustc --edition 2021 examples/rust/options/option_handling.rs && ./option_handling
```

Where an example could not be executed on the authoring machine, its header says
`validated by inspection` so you know the difference.

## Finding something specific

- [`../TOPICS.md`](../TOPICS.md) — every example with its date, difficulty and
  category, in one table.
- [`../progress.json`](../progress.json) — the same data, machine-readable.
