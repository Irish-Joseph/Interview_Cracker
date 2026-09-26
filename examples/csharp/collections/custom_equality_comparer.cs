/*
Topic: Custom equality for Dictionary and HashSet.
Concepts: IEqualityComparer<T>, case-insensitive keys, hash/equality contract.
Run: dotnet-script custom_equality_comparer.cs
NOTE: validated by inspection (no C# toolchain on this host).
Expected output: unique emails: 2; ada count: 2
*/

using System;
using System.Collections.Generic;

sealed class EmailComparer : IEqualityComparer<string>
{
    public bool Equals(string? left, string? right) =>
        StringComparer.OrdinalIgnoreCase.Equals(left?.Trim(), right?.Trim());

    public int GetHashCode(string value) =>
        StringComparer.OrdinalIgnoreCase.GetHashCode(value.Trim());
}

var comparer = new EmailComparer();
var counts = new Dictionary<string, int>(comparer);

foreach (var email in new[] { "Ada@example.com", " ada@EXAMPLE.com ", "grace@example.com" })
{
    counts.TryGetValue(email, out var count);
    counts[email] = count + 1;
}

if (counts.Count != 2 || counts["ADA@example.com"] != 2)
    throw new InvalidOperationException("equality and hashing disagree");

Console.WriteLine($"unique emails: {counts.Count}; ada count: {counts["ada@example.com"]}");
