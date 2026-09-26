# Runnable Examples

213 focused programs across 13 languages. Each file teaches one concept and
includes its run command, expected behavior, and validation status.

## Find an example

Examples use `examples/<language>/<category>/<descriptive_name>.<ext>`.
Browse every entry in [TOPICS.md](../TOPICS.md), or query the same data from
[progress.json](../progress.json).

| Language | Examples | Categories |
|---|---:|---|
| [Python](python/) | 24 | algorithms, basics, collections, context-managers, data-models, dates, decorators, files, functions, generators, json, numbers, oop, standard-library, strings, typing |
| [SQL](sql/) | 19 | aggregation, constraints, dates, filters, joins, recursive-ctes, set-operations, strings, subqueries, transactions, window-functions |
| [Rust](rust/) | 19 | basics, closures, collections, concurrency, enums, error-handling, iterators, lifetimes, matching, modules, options, ownership, strings, traits |
| [JavaScript](javascript/) | 18 | arrays, async, basics, collections, errors, generators, objects, strings, utilities |
| [Go](go/) | 18 | algorithms, concurrency, data-structures, error-handling, errors, files, generics, interfaces, json, maps, slices, sorting, structs, testing |
| [C](c/) | 18 | arrays, basics, data-structures, files, functions, pointers, strings |
| [Java](java/) | 17 | algorithms, collections, concurrency, enums, error-handling, exceptions, generics, interfaces, oop, optional, records, streams, strings |
| [C++](cpp/) | 16 | algorithms, data-structures, error-handling, oop, operators, raii, smart-pointers, stl, strings, sum-types, templates |
| [TypeScript](typescript/) | 17 | advanced-types, async, basics, classes, enums, generics, interfaces, narrowing, unions, utility-types |
| [Bash](bash/) | 16 | arrays, basics, functions, scripting, testing, utilities |
| [C#](csharp/) | 15 | async, basics, collections, delegates, error-handling, generics, linq, methods, nullability, oop, patterns, strings |
| [Ruby](ruby/) | 9 | basics, blocks, enumerable, files, methods, oop, pattern-matching |
| [PowerShell](powershell/) | 7 | basics, data, error-handling, functions, objects, text |

## Run them

Most examples have no dependencies:

```bash
python examples/python/functions/mutable_default_arguments.py
node examples/javascript/async/abort_controller_cancellation.js
node --experimental-strip-types examples/typescript/advanced-types/branded_types.ts
```

Compiled-language examples include the exact command in their header. If the
authoring host lacked a toolchain, the file says `validated by inspection`
instead of pretending it was run.

> This table is generated from `progress.json`; keep it synchronized with the
> registry when adding examples.
