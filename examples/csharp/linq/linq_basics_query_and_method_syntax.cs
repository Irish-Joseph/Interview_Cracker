// Topic: LINQ basics — query syntax vs method syntax.
//
// Concepts:
// - LINQ method syntax (Where, Select, OrderBy, GroupBy)
// - LINQ query syntax (from/where/select) and when they match
// - Aggregation: Count, Sum, Average, Min, Max
// - Joins between two collections
// - Lazy evaluation: the query runs on enumeration
//
// Both syntaxes compile to the same extension methods; method
// syntax composes better in pipelines, query syntax reads closer
// to SQL. Pick one style per codebase.
//
// Run:  dotnet run   (or compile with csc)
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

using System;
using System.Collections.Generic;
using System.Linq;

public record Product(string Name, string Category, decimal Price, int Stock);
public record Order(string Customer, string ProductName, int Units);

public class LinqBasics
{
    public static void Main()
    {
        var products = new List<Product>
        {
            new ("Keyboard",  "peripherals", 45m,  12),
            new ("Mouse",     "peripherals", 25m,  30),
            new ("Monitor",   "displays",   220m,   5),
            new ("Webcam",    "peripherals", 60m,   0),
            new ("Stand",     "accessories", 35m,  20),
        };

        var orders = new List<Order>
        {
            new ("Acme",   "Keyboard", 2),
            new ("Globex", "Mouse",    5),
            new ("Acme",   "Monitor",  1),
            new ("Initech","Mouse",    3),
        };

        // --- 1. Method syntax: filter + project + sort -------------------
        var cheapPeripherals = products
            .Where(p => p.Category == "peripherals" && p.Price < 50m)
            .OrderBy(p => p.Price)
            .Select(p => p.Name);

        Console.WriteLine("cheap peripherals: " + string.Join(", ", cheapPeripherals));
        // -> Mouse, Keyboard

        // --- 2. Query syntax: same shape as SQL --------------------------
        var inStock =
            from p in products
            where p.Stock > 10
            orderby p.Name
            select p.Name;

        Console.WriteLine("well stocked: " + string.Join(", ", inStock));
        // -> Keyboard, Mouse, Stand

        // --- 3. Aggregation ----------------------------------------------
        Console.WriteLine($"average price: {products.Average(p => p.Price):0.00}");
        // -> 57.00
        Console.WriteLine($"total stock:   {products.Sum(p => p.Stock)}");
        // -> 67

        // Units ordered per product (group + aggregate).
        var unitsByProduct = orders
            .GroupBy(o => o.ProductName)
            .Select(g => new { Product = g.Key, Units = g.Sum(o => o.Units) })
            .OrderByDescending(x => x.Units);

        foreach (var row in unitsByProduct)
            Console.WriteLine($"{row.Product}: {row.Units} units");
        // Mouse: 8 units
        // Keyboard: 2 units
        // Monitor: 1 units

        // --- 4. Join orders with products ---------------------------------
        var report =
            from o in orders
            join p in products on o.ProductName equals p.Name
            where p.Stock > 0
            select new
            {
                o.Customer,
                o.ProductName,
                Total = o.Units * (int)p.Price,
            };

        foreach (var line in report)
            Console.WriteLine($"{line.Customer} - {line.ProductName}: ${line.Total}");
        // Acme - Keyboard: $90
        // Globex - Mouse: $125
        // Acme - Monitor: $220
        // Initech - Mouse: $75
        // (Webcam has stock = 0, so any Webcam order would be filtered out.)
    }
}
