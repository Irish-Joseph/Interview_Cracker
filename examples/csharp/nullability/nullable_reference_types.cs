// Topic: Nullable reference types - making null a compile-time concern.
//
// Before C# 8 every reference could be null and the compiler said nothing.
// With nullable reference types enabled, `string` means "never null" and
// `string?` means "may be null" -- and the compiler warns when you get it
// wrong. It is a WARNING system, not a runtime guarantee: nothing stops a
// null arriving from an older library or from JSON deserialisation.
//
// Concepts:
// - #nullable enable, and what string vs string? now mean
// - Null-conditional ?. and null-coalescing ?? / ??=
// - The null-forgiving operator ! and why it is a last resort
// - required / init members
// - Nullable VALUE types (int?) vs nullable REFERENCE types (string?)
// - Pattern matching against null: is null / is not null
// - ArgumentNullException.ThrowIfNull at trust boundaries
//
// Run:  dotnet run
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace Learning.Nullability;

public class Address
{
    public required string City { get; init; }   // required: must be set
    public string? Postcode { get; init; }       // genuinely optional
}

public class Customer
{
    public required string Name { get; init; }
    public Address? Address { get; init; }       // may legitimately be absent
    public List<string> Tags { get; init; } = new();   // never null, may be empty
}

public static class Program
{
    // `string` PROMISES a non-null return; the compiler checks every path.
    private static string Describe(Customer customer)
        => $"{customer.Name} ({customer.Address?.City ?? "no city"})";

    // `string?` documents that null is a normal outcome, forcing callers to
    // deal with it.
    private static string? FindPostcode(Customer customer)
        => customer.Address?.Postcode;

    private static int PostcodeLength(Customer customer)
    {
        // ?. short-circuits the WHOLE chain to null if any link is null.
        // Without it this needs two nested null checks.
        return customer.Address?.Postcode?.Length ?? 0;
    }

    private static void EnsureTag(Customer customer, string tag)
    {
        if (!customer.Tags.Contains(tag))
        {
            customer.Tags.Add(tag);
        }
    }

    // Public APIs still receive null from callers that ignore the warnings,
    // or from code compiled without nullable enabled. Guard anyway.
    public static string Normalise(string? raw)
    {
        ArgumentNullException.ThrowIfNull(raw);
        // After the guard the compiler KNOWS raw is non-null: no warning below.
        return raw.Trim().ToLowerInvariant();
    }

    private static string Explain(string? value)
    {
        // `is null` reads better than == and cannot be fooled by an
        // overloaded == operator.
        if (value is null)
        {
            return "was null";
        }
        // The compiler has narrowed `value` to non-null on this path.
        return $"{value.Length} characters";
    }

    public static void Main()
    {
        var withAddress = new Customer
        {
            Name = "Ada",
            Address = new Address { City = "London", Postcode = "NW1 2DB" },
        };
        var withoutAddress = new Customer { Name = "Grace" };
        var addressNoPostcode = new Customer
        {
            Name = "Alan",
            Address = new Address { City = "Hampton" },
        };

        Console.WriteLine("-- ?. collapses a whole chain --");
        foreach (var customer in new[] { withAddress, withoutAddress, addressNoPostcode })
        {
            Console.WriteLine($"  {Describe(customer)}");
            Console.WriteLine($"    postcode: {FindPostcode(customer) ?? "<none>"}, "
                              + $"length: {PostcodeLength(customer)}");
        }

        Console.WriteLine("-- guarding at the boundary --");
        Console.WriteLine($"  Normalise(\"  MiXeD  \") = \"{Normalise("  MiXeD  ")}\"");
        try
        {
            // `null!` uses the null-forgiving operator to silence the warning
            // so we can demonstrate the runtime guard. Do not do this for real.
            Normalise(null!);
        }
        catch (ArgumentNullException error)
        {
            Console.WriteLine($"  Normalise(null) threw {error.GetType().Name} (param: {error.ParamName})");
        }

        Console.WriteLine("-- flow analysis narrows the type --");
        foreach (var value in new string?[] { "hello", null, "" })
        {
            Console.WriteLine($"  {(value is null ? "null" : $"\"{value}\"")} -> {Explain(value)}");
        }

        Console.WriteLine("-- nullable value types are different --");
        // int? is Nullable<int>, a STRUCT with HasValue/Value, and a runtime
        // feature since C# 2. string? is only an annotation the compiler
        // tracks -- at runtime it is an ordinary string.
        int? maybeNumber = null;
        Console.WriteLine($"  int? HasValue      : {maybeNumber.HasValue}");
        Console.WriteLine($"  GetValueOrDefault(): {maybeNumber.GetValueOrDefault(-1)}");
        maybeNumber = 7;
        Console.WriteLine($"  after assignment   : {maybeNumber.Value}");
        Console.WriteLine($"  typeof(int?)       : {typeof(int?).Name}");
        Console.WriteLine($"  typeof(string)     : {typeof(string).Name} (the ? is erased)");

        Console.WriteLine("-- collections: empty, not null --");
        EnsureTag(withoutAddress, "prospect");
        Console.WriteLine($"  tags: [{string.Join(", ", withoutAddress.Tags)}]");
        // Returning an empty collection instead of null removes a whole class
        // of null checks from every caller.
        Console.WriteLine($"  any tags on Ada? {withAddress.Tags.Any()}");

        Console.WriteLine("-- the null-forgiving operator --");
        // ! tells the compiler "trust me". It generates NO runtime check, so
        // if you are wrong you get a NullReferenceException exactly as before.
        string? risky = "actually fine";
        Console.WriteLine($"  risky!.Length = {risky!.Length} (no runtime check was added)");
    }
}

/* Expected output:
-- ?. collapses a whole chain --
  Ada (London)
    postcode: NW1 2DB, length: 7
  Grace (no city)
    postcode: <none>, length: 0
  Alan (Hampton)
    postcode: <none>, length: 0
-- guarding at the boundary --
  Normalise("  MiXeD  ") = "mixed"
  Normalise(null) threw ArgumentNullException (param: raw)
-- flow analysis narrows the type --
  "hello" -> 5 characters
  null -> was null
  "" -> 0 characters
-- nullable value types are different --
  int? HasValue      : False
  GetValueOrDefault(): -1
  after assignment   : 7
  typeof(int?)       : Nullable`1
  typeof(string)     : String (the ? is erased)
-- collections: empty, not null --
  tags: [prospect]
  any tags on Ada? False
-- the null-forgiving operator --
  risky!.Length = 13 (no runtime check was added)
*/
