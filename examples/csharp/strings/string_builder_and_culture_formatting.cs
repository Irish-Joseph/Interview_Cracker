// Topic: Strings, StringBuilder, and culture-aware formatting in C#.
//
// Concepts:
// - Strings are IMMUTABLE: every "change" allocates a new string
// - StringBuilder for repeated mutation (appends, inserts) in a loop
// - Interpolation $"..." and string.Join
// - Culture-aware formatting: dates/numbers differ per locale; invariant
//   culture for machine-readable output, UI culture for display
// - Ordinal vs linguistic comparison (string.Compare overloads)
//
// Validated by inspection (no .NET SDK on the authoring machine).
//
// Expected output:
//   a is still: hello
//   built: a-b-c-d
//   capacity 16 vs length 7
//   joined: a | b | c | d
//   invariant: 2026-09-21 13:05:00  |  1234.5 -> 1,234.50
//   de-DE: 21.09.2026 13:05:00  |  1234.5 -> 1.234,50
//   compare("a","B") ordinal = 1   (a is after B in code-point order)
//   compare("a","B") linguistic = -1  (case is a secondary factor)

using System;
using System.Globalization;
using System.Text;

class StringsAndFormatting
{
    static void Main()
    {
        // --- Immutability: each + creates a NEW string ---------------
        string a = "hello";
        string b = a + " world";   // new string; `a` is unchanged
        Console.WriteLine($"a is still: {a}");

        // --- StringBuilder: one buffer, many mutations ---------------
        var sb = new StringBuilder();
        string[] parts = { "a", "b", "c", "d" };
        for (int i = 0; i < parts.Length; i++)
        {
            if (i > 0) sb.Append('-');
            sb.Append(parts[i]);
        }
        Console.WriteLine($"built: {sb}");          // a-b-c-d
        Console.WriteLine($"capacity {sb.Capacity} vs length {sb.Length}");

        // --- Join: the idiomatic way to glue sequences ---------------
        Console.WriteLine($"joined: {string.Join(" | ", parts)}");   // a | b | c | d

        // --- Culture-aware formatting --------------------------------
        DateTime dt = new(2026, 9, 21, 13, 5, 0);
        double money = 1234.5;

        // Invariant: stable, machine-readable — use for files/logs/DB.
        string invDate = dt.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture);
        string invNum  = money.ToString("N2", CultureInfo.InvariantCulture);
        Console.WriteLine($"invariant: {invDate}  |  {money} -> {invNum}");

        // UI culture: what a human in that locale expects.
        string uiDate = dt.ToString("G", new CultureInfo("de-DE"));   // 21.09.2026 13:05:00
        string uiNum  = money.ToString("N2", new CultureInfo("de-DE")); // 1.234,50
        Console.WriteLine($"de-DE: {uiDate}  |  {money} -> {uiNum}");

        // --- Comparison: ordinal vs linguistic -----------------------
        // Ordinal: by UTF-16 code unit. 'a'(97) > 'B'(66) -> 1.
        int ordinal = string.Compare("a", "B", StringComparison.Ordinal);
        Console.WriteLine($"compare(\"a\",\"B\") ordinal = {ordinal}");

        // Linguistic (current culture): case is a secondary factor,
        // so 'a' sorts before 'B'.
        int linguistic = string.Compare("a", "B", StringComparison.CurrentCulture);
        Console.WriteLine($"compare(\"a\",\"B\") linguistic = {linguistic}");
    }
}
