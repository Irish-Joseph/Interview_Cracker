# Examples

163 focused, runnable programs across 13 languages. **One concept per
file** - each is small enough to read in a sitting, and most print their own
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
what they teach - there are no `example1.py` files here.

Every file opens with a header stating the topic, the concepts it demonstrates,
and its expected output, so you can tell whether it is what you want without
running it.

## Languages

| Language | Examples | Categories |
|---|---|---|
| [Python](python/) | 21 | `algorithms`, `basics`, `collections`, `context-managers`, `data-models`, `dates`, `decorators`, `files`, `generators`, `json`, `oop`, `standard-library`, `strings`, `typing` |
| [SQL](sql/) | 15 | `aggregation`, `dates`, `filters`, `joins`, `recursive-ctes`, `set-operations`, `strings`, `subqueries`, `transactions`, `window-functions` |
| [Go](go/) | 14 | `algorithms`, `concurrency`, `data-structures`, `errors`, `files`, `generics`, `interfaces`, `maps`, `slices`, `sorting`, `structs`, `testing` |
| [JavaScript](javascript/) | 14 | `arrays`, `async`, `basics`, `collections`, `errors`, `generators`, `objects`, `strings`, `utilities` |
| [Rust](rust/) | 14 | `basics`, `closures`, `collections`, `concurrency`, `enums`, `error-handling`, `iterators`, `lifetimes`, `matching`, `modules`, `options`, `ownership`, `strings`, `traits` |
| [Bash](bash/) | 13 | `arrays`, `basics`, `functions`, `scripting`, `testing`, `utilities` |
| [C](c/) | 13 | `arrays`, `basics`, `data-structures`, `files`, `pointers`, `strings` |
| [Java](java/) | 13 | `algorithms`, `collections`, `concurrency`, `exceptions`, `generics`, `interfaces`, `oop`, `optional`, `records`, `streams`, `strings` |
| [C++](cpp/) | 12 | `algorithms`, `data-structures`, `error-handling`, `operators`, `raii`, `smart-pointers`, `stl`, `strings`, `sum-types`, `templates` |
| [C#](csharp/) | 12 | `async`, `basics`, `collections`, `delegates`, `error-handling`, `generics`, `linq`, `methods`, `nullability`, `patterns`, `strings` |
| [TypeScript](typescript/) | 12 | `advanced-types`, `async`, `basics`, `classes`, `enums`, `generics`, `interfaces`, `narrowing`, `unions`, `utility-types` |
| [Ruby](ruby/) | 6 | `basics`, `blocks`, `files`, `oop`, `pattern-matching` |
| [PowerShell](powershell/) | 4 | `data`, `error-handling`, `functions`, `objects` |

## Running them

Most examples are self-contained with no dependencies:

```bash
python examples/python/standard-library/functools_essentials.py
node    examples/javascript/arrays/array_methods_tour.js
bash    examples/bash/basics/conditionals_and_tests.sh
```

Compiled languages need the usual toolchain:

```bash
gcc -Wall examples/c/basics/command_line_arguments.c -o demo && ./demo
g++ -std=c++20 examples/cpp/stl/map_and_set_containers.cpp -o demo && ./demo
go  run examples/go/structs/structs_embedding_and_json.go
rustc --edition 2021 examples/rust/collections/vec_and_hashmap.rs && ./vec_and_hashmap
```

TypeScript examples run under Node 22+:

```bash
node --experimental-strip-types examples/typescript/basics/satisfies_operator.ts
node --experimental-transform-types examples/typescript/enums/enums_vs_literal_unions.ts
```

Where an example could not be executed on the authoring machine, its header says
`validated by inspection` so you know the difference.

## Finding something specific

- [`../TOPICS.md`](../TOPICS.md) - every example with its date, difficulty and
  category, in one table.
- [`../progress.json`](../progress.json) - the same data, machine-readable.

> This file is generated from `progress.json`. Regenerate it rather than editing
> the table by hand, so the counts cannot drift.
