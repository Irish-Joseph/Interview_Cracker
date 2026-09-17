// Topic: Deferred execution — LINQ queries run when enumerated, not when written.
//
// Concepts:
// - Query syntax vs method syntax producing the SAME lazy sequence
// - A query builds an execution plan; it runs only on enumeration
//   (foreach, ToList, Count, ...)
// - Each enumeration RE-RUNS the pipeline (no built-in caching)
// - Observable side effects prove when code actually executes
//
// Example output:
//   (no logs yet — the query has not run)
//   [eval] 3
//   [eval] 6
//   [eval] 9
//   [eval] 12
//   12
//   24
//   36
//   48
//   [eval] 3
//   [eval] 6
//   [eval] 9
//   [eval] 12
//   count: 4
//   (second enumeration re-runs everything)
//   [eval] 3
//   [eval] 6
//   [eval] 9
//   [eval] 12
//   12 24 36 48

using System;
using System.Collections.Generic;
using System.Linq;

class DeferredExecution
{
    static void Main()
    {
        List<int> numbers = new() { 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13 };

        // Method-syntax pipeline. Nothing executes until we enumerate:
        // each Where/Select returns a new enumerable that wraps the
        // previous step into a single lazily-evaluated chain.
        var pipeline = numbers
            .Where(n =>
            {
                Console.WriteLine($"[eval] {n}"); // proves execution time
                return n % 3 == 0;
            })
            .Select(n => n * 4);

        // Query syntax is just sugar for the same pipeline:
        // var query = from n in numbers where n % 3 == 0 select n * 4;

        Console.WriteLine("(no logs yet — the query has not run)");

        // First enumeration: the whole chain runs once per element.
        foreach (int value in pipeline)
        {
            Console.WriteLine(value);
        }

        // Count also triggers a full pass:
        Console.WriteLine($"count: {pipeline.Count()}");

        // Enumerating AGAIN re-runs everything — deferred queries are
        // not cached. Call .ToList() to materialize and cache results.
        Console.WriteLine("(second enumeration re-runs everything)");
        var cached = pipeline.ToList();
        foreach (int value in cached)
        {
            Console.Write(value + " ");
        }
        Console.WriteLine();
    }
}
