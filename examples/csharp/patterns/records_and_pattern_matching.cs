// Topic: Records and pattern matching in C#.
//
// Concepts:
// - record: immutable-by-default data type with value equality
// - Positional records: (int X, int Y) syntax
// - with-expressions: copy with modification
// - Pattern matching: is, property patterns, relational patterns
// - Switch expressions with patterns (exhaustive-ish)
// - Null patterns: is null / is not null
//
// Records shine for "data carriers"; pattern matching shines for
// "deciding what a value is/means" — together they replace a lot
// of if-else chains and manual Equals/ToString boilerplate.
//
// Run:  dotnet run
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

using System;

// A positional record: the compiler generates constructor,
// deconstruction, Equals, GetHashCode and ToString.
public record Point(int X, int Y);

// Inheritance: a record can extend another record.
public record Vector(int X, int Y, int Z) : Point(X, Y);

public class RecordsAndPatterns
{
    public static void Main()
    {
        // --- 1. Value equality: same fields == equal objects -------------------
        Point p1 = new Point(1, 2);
        Point p2 = new Point(1, 2);
        Point p3 = new(3, 4);

        Console.WriteLine($"p1 == p2: {p1 == p2}");   // True  (value equality!)
        Console.WriteLine($"p1 == p3: {p1 == p3}");   // False
        // Reference types normally compare by REFERENCE; records
        // compare by VALUE. That's the big behavioral difference.

        // --- 2. with-expression: immutable copy with one field changed ---------
        Point moved = p1 with { Y = 9 };
        Console.WriteLine($"p1 = {p1}");     // (1, 2)   unchanged
        Console.WriteLine($"moved = {moved}"); // (1, 9) new instance

        // --- 3. Record inheritance + ToString ----------------------------------
        Vector v = new Vector(1, 2, 3);
        Console.WriteLine($"vector: {v}");
        // -> vector: Vector { X = 1, Y = 2, Z = 3 }

        // --- 4. is-patterns: type + value checks in one step ---------------------
        object shapes = new object[]
        {
            42,
            "hello",
            3.14,
            new Point(5, 6),
            null,
        };

        foreach (object shape in shapes)
        {
            string description = shape switch
            {
                null                 => "nothing",
                int i when i > 0     => $"positive int ({i})",
                int i                => $"non-positive int ({i})",
                double d             => $"double ({d})",
                string s             => $"string ('{s}')",
                Point { X: > 0 } pt  => $"positive-x point {pt}",
                Point pt             => $"point {pt}",
                _                    => $"unknown {shape.GetType().Name}",
            };
            Console.WriteLine($"  {description}");
        }
        // ->   positive int (42)
        //      string ('hello')
        //      double (3.14)
        //      positive-x point (5, 6)
        //      nothing

        // --- 5. Destructuring: pull fields out of a record -------------------------
        Point decon = p3;
        if (decon is { X: int x, Y: int y })
        {
            Console.WriteLine($"destructured: x={x}, y={y}, sum={x + y}");
            // -> destructured: x=3, y=4, sum=7
        }

        // --- 6. Pattern guards (when) keep logic honest ----------------------------
        int code = 418;
        string verdict = code switch
        {
            >= 200 and < 300 => "success",
            >= 400 and < 500 => "client error",
            >= 500           => "server error",
            _                => "other",
        };
        Console.WriteLine($"HTTP {code}: {verdict}");
        // -> HTTP 418: client error
    }
}
