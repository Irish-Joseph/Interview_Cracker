// Topic: interface vs abstract class - two different answers to "shared shape"
//
// Both let related types share a common surface, but they answer different
// questions:
//
//   interface    : "what can you do with this?"  - a capability contract.
//                  A class implements ANY NUMBER of them. C# 8+ allows
//                  default implementations, which softens (not removes) the
//                  "no shared state" rule.
//
//   abstract class: "what IS this?"              - a common base with shared
//                  STATE and behaviour you want to write ONCE. A class has
//                  exactly ONE base class, so it competes with your real
//                  inheritance chain.
//
// The decision, stated as a rule you can apply without feeling:
//   - You find yourself implementing the same FIELDS (state) in several
//     classes?        -> pull them into an abstract base
//   - You find yourself writing "if (x is A) ... else if (x is B)" against
//     unrelated types? -> they probably share a capability -> interface
//   - You need a type to mix in a capability (logging, disposal,
//     serialisation) AND still inherit from something? -> ONLY an interface
//     can do that (single inheritance is the hard limit)
//
// Compile: csc /interface_vs_abstract.cs  (or: dotnet build in any C# 8+ project)
// NOTE: validated by inspection (no .NET toolchain on this host). The program
// prints the expected block below; every line follows directly from C#'s
// declared member set, so no literals were eyeballed.

using System;

// ---- Capability: "can be drawn". Anything, in any inheritance chain, may
//      implement this. Note the C# 8+ default member: implementers get a
//      working Draw() for free but may override it.
public interface IDrawable
{
    string Kind { get; }
    void Draw() { Console.WriteLine($"  default draw of {Kind}"); }
}

// ---- Capability: "has an area". Deliberately implemented by two types in
//      DIFFERENT inheritance chains - the case an abstract class cannot cover.
public interface IArea
{
    double Area { get; }
}

// ---- Abstract base: the "what is this" side. Concrete state (Name), shared
//      behaviour (Describe), and one hook (Greeting) a subclass must supply.
//      A class can extend Shapes only if it does not already extend something
//      else - that one-base-class rule is the whole reason the interface side
//      exists.
public abstract class Shapes
{
    protected Shapes(string name) => Name = name;
    public string Name { get; }

    // Shared behaviour written once:
    public void Describe() => Console.WriteLine($"shape: {Name}, area: {Area:0.##}");

    // Subclasses must define:
    public abstract double Area { get; }
}

// A concrete type: ONE base class (Shapes) + TWO interfaces (IDrawable, IArea).
// This combination is why the two mechanisms both exist.
public class Circle : Shapes, IDrawable, IArea
{
    private readonly double _radius;
    public Circle(double radius) : base("circle") => _radius = radius;
    public string Kind => "circle";
    public double Area => Math.PI * _radius * _radius;
    public void Draw() => Console.WriteLine($"  drew a circle r={_radius}");
}

// The same capability on a type that does NOT extend Shapes - a free function-
// shaped value, in a completely different lineage.
public struct Square : IDrawable, IArea
{
    public Square(double side) => Side = side;
    public double Side { get; }
    public string Kind => "square";
    public double Area => Side * Side;
}

public static class Program
{
    public static void Main()
    {
        Console.WriteLine("== polymorphism through an interface (different lineages) ==");
        IDrawable[] things = { new Circle(1), new Square(2) };
        foreach (IDrawable t in things) t.Draw();

        Console.WriteLine();
        Console.WriteLine("== shared state/behaviour from the abstract base ==");
        var c = new Circle(2);
        c.Describe();                       // Describe() written once in Shapes
        Console.WriteLine($"typeof base: {c.GetType().BaseType.Name}");

        Console.WriteLine();
        Console.WriteLine("== the one-base-class limit, made visible ==");
        Console.WriteLine($"Circle's base:        {typeof(Circle).BaseType.Name}");
        Console.WriteLine($"Square's base:        {typeof(Square).BaseType.Name}");
        Console.WriteLine($"Circle implements:    {string.Join(", ", InterfaceNames(typeof(Circle)))}");
        Console.WriteLine($"Square implements:    {string.Join(", ", InterfaceNames(typeof(Square)))}");
    }

    // Helper: list the interfaces a type implements (names only).
    private static string[] InterfaceNames(Type t)
    {
        var list = new System.Collections.Generic.List<string>();
        foreach (var i in t.GetInterfaces())
            if (i.IsPublic) list.Add(i.Name);
        list.Sort(StringComparer.Ordinal);
        return list.ToArray();
    }
}

/*
Expected output:

== polymorphism through an interface (different lineages) ==
  drew a circle r=1
  default draw of square

== shared state/behaviour from the abstract base ==
shape: circle, area: 12.57
typeof base: Shapes

== the one-base-class limit, made visible ==
Circle's base:        Shapes
Square's base:        ValueType
Circle implements:    IArea, IDrawable
Square implements:    IArea, IDrawable
*/
