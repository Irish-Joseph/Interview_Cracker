// Topic: C# core collections — List<T>, Dictionary<K,V> and HashSet<T>.
//
// Concepts:
// - List<T>: ordered, indexable, grows automatically
// - Dictionary<K,V>: key -> value, and the TryGetValue pattern
// - HashSet<T>: uniqueness and set algebra (union, intersect, except)
// - Collection initializers and the index initializer syntax
// - Why the lookup collections are O(1) and List.Contains is O(n)
// - Choosing between them, and the equality rules that make them work
//
// The decision guide:
//   ordered, duplicates allowed, index access -> List<T>
//   look something up by a key                -> Dictionary<K,V>
//   membership and uniqueness only            -> HashSet<T>
//   first-in-first-out / last-in-first-out    -> Queue<T> / Stack<T>
//
// Run:  dotnet run
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

using System;
using System.Collections.Generic;
using System.Linq;

class CoreCollectionsDemo
{
    static void Main()
    {
        ListBasics();
        DictionaryBasics();
        HashSetBasics();
        ChoosingTheRightOne();
    }

    // --- 1. List<T> --------------------------------------------------------

    static void ListBasics()
    {
        Console.WriteLine("1. List<T>");

        // Collection initializer; the capacity grows as needed.
        var tasks = new List<string> { "design", "build", "test" };

        tasks.Add("deploy");
        tasks.Insert(0, "plan");          // O(n): everything shifts right
        tasks.Remove("build");            // removes the FIRST match

        Console.WriteLine($"   items:      {string.Join(" -> ", tasks)}");
        Console.WriteLine($"   count:      {tasks.Count}");
        Console.WriteLine($"   index 0:    {tasks[0]}");
        Console.WriteLine($"   contains:   {tasks.Contains("test")}");   // O(n) scan
        Console.WriteLine($"   index of:   {tasks.IndexOf("test")}");

        // Removing while iterating throws. Filter into a new list instead,
        // or iterate backwards by index.
        var remaining = tasks.Where(t => t != "deploy").ToList();
        Console.WriteLine($"   filtered:   {string.Join(", ", remaining)}");

        // Sorting in place, with a comparison delegate for custom orders.
        var numbers = new List<int> { 42, 7, 93, 8 };
        numbers.Sort();
        Console.WriteLine($"   sorted:     {string.Join(", ", numbers)}");
        numbers.Sort((a, b) => b.CompareTo(a));
        Console.WriteLine($"   descending: {string.Join(", ", numbers)}");
    }

    // --- 2. Dictionary<K,V> ------------------------------------------------

    static void DictionaryBasics()
    {
        Console.WriteLine("\n2. Dictionary<K,V>");

        var stock = new Dictionary<string, int>
        {
            ["apples"] = 12,
            ["pears"] = 3,
            ["plums"] = 0,
        };

        stock["apples"] = 15;             // the indexer updates OR inserts
        stock.Add("figs", 7);             // Add THROWS if the key exists

        // TryAdd returns false instead of throwing on a duplicate key.
        Console.WriteLine($"   TryAdd duplicate: {stock.TryAdd("figs", 99)}");

        // Reading an absent key with the indexer throws. TryGetValue is the
        // idiomatic single-lookup read:
        if (stock.TryGetValue("pears", out int pears))
        {
            Console.WriteLine($"   pears:            {pears}");
        }
        Console.WriteLine($"   missing key:      {(stock.TryGetValue("kiwi", out int kiwi) ? kiwi.ToString() : "not stocked")}");

        // ContainsKey followed by the indexer costs TWO lookups — prefer
        // TryGetValue when you need the value as well.
        Console.WriteLine($"   ContainsKey:      {stock.ContainsKey("plums")}");

        // Counting with a dictionary: the classic tally loop.
        var votes = new[] { "red", "blue", "red", "green", "red", "blue" };
        var tally = new Dictionary<string, int>();
        foreach (var vote in votes)
        {
            tally[vote] = tally.GetValueOrDefault(vote) + 1;
        }
        foreach (var (colour, count) in tally.OrderByDescending(p => p.Value))
        {
            Console.WriteLine($"   {colour,-6} {count}");
        }

        // Iteration order is NOT guaranteed — sort explicitly when it matters.
        Console.WriteLine($"   keys sorted:      {string.Join(", ", stock.Keys.OrderBy(k => k))}");
    }

    // --- 3. HashSet<T> -----------------------------------------------------

    static void HashSetBasics()
    {
        Console.WriteLine("\n3. HashSet<T>");

        var frontend = new HashSet<string> { "ana", "ben", "cara" };
        var backend = new HashSet<string> { "cara", "dev", "ana" };

        // Add returns false when the item was already present — a cheap way
        // to detect duplicates in a single pass.
        Console.WriteLine($"   Add existing:  {frontend.Add("ana")}");
        Console.WriteLine($"   Contains:      {frontend.Contains("ben")}");   // O(1)

        // The mutating set operations change the set they are called on,
        // so work on a copy when the original is still needed.
        var both = new HashSet<string>(frontend);
        both.IntersectWith(backend);
        var either = new HashSet<string>(frontend);
        either.UnionWith(backend);
        var frontendOnly = new HashSet<string>(frontend);
        frontendOnly.ExceptWith(backend);

        Console.WriteLine($"   union:         {Show(either)}");
        Console.WriteLine($"   intersection:  {Show(both)}");
        Console.WriteLine($"   frontend only: {Show(frontendOnly)}");
        Console.WriteLine($"   is subset:     {both.IsSubsetOf(frontend)}");

        // Deduplicating a list, preserving nothing about order:
        var withDupes = new List<int> { 3, 1, 3, 2, 1, 3 };
        Console.WriteLine($"   deduped:       {Show(new HashSet<int>(withDupes).Select(n => n.ToString()))}");
    }

    static string Show(IEnumerable<string> items) =>
        "{" + string.Join(", ", items.OrderBy(i => i)) + "}";

    // --- 4. Picking one ----------------------------------------------------

    static void ChoosingTheRightOne()
    {
        Console.WriteLine("\n4. lookup cost");

        var ids = Enumerable.Range(0, 200_000).ToList();
        var idSet = new HashSet<int>(ids);
        const int needle = 199_999;      // worst case: the very last item

        var clock = System.Diagnostics.Stopwatch.StartNew();
        for (int i = 0; i < 200; i++) { _ = ids.Contains(needle); }
        var listTime = clock.Elapsed.TotalMilliseconds;

        clock.Restart();
        for (int i = 0; i < 200; i++) { _ = idSet.Contains(needle); }
        var setTime = clock.Elapsed.TotalMilliseconds;

        Console.WriteLine($"   200x List.Contains:    {listTime:F2} ms  (O(n) each)");
        Console.WriteLine($"   200x HashSet.Contains: {setTime:F2} ms  (O(1) each)");

        // Equality note: Dictionary and HashSet rely on GetHashCode and
        // Equals. Reference types use identity by default, so two "equal"
        // custom objects are two different keys unless the type overrides
        // both — or is a record, which does it for you.
        Console.WriteLine("\n   records get value equality for free:");
        var a = new Point(1, 2);
        var b = new Point(1, 2);
        var seen = new HashSet<Point> { a, b };
        Console.WriteLine($"   a == b: {a == b}, distinct entries: {seen.Count}");
    }

    record Point(int X, int Y);
}
