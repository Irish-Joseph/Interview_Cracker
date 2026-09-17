// Topic: Generic classes, constraints, and covariance/contravariance.
//
// C# generics are REIFIED: the type argument survives to runtime, unlike
// Java's erasure. That is why typeof(List<int>) != typeof(List<string>),
// why you can write `new T()`, and why `default(T)` knows what it means.
//
// Concepts:
// - Generic classes and methods, with type inference at the call site
// - Constraints: where T : class / struct / new() / IComparable<T> / notnull
// - default(T) and why it differs for value and reference types
// - Covariance (out) and contravariance (in) on interfaces
// - Why IList<T> is invariant while IEnumerable<T> is covariant
//
// Run:  dotnet run
//
// NOTE: validated by inspection (no .NET SDK on authoring host).

#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace Learning.Generics;

// ---------------------------------------------------------------------------
// 1. A generic class with a constraint
// ---------------------------------------------------------------------------

// `where T : IComparable<T>` is what allows CompareTo below. Without it the
// compiler only knows T is *some* type, so it offers no operations at all.
public class BoundedList<T> where T : IComparable<T>
{
    private readonly List<T> _items = new();

    public int Capacity { get; }

    public BoundedList(int capacity)
    {
        if (capacity < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(capacity));
        }
        Capacity = capacity;
    }

    public bool TryAdd(T item)
    {
        if (_items.Count >= Capacity)
        {
            return false;
        }
        _items.Add(item);
        return true;
    }

    // The constraint makes CompareTo available.
    public T? Max()
    {
        if (_items.Count == 0)
        {
            // default(T) is null for reference types and the zero value for
            // value types -- 0 for int, false for bool, a zeroed struct.
            return default;
        }

        T best = _items[0];
        foreach (T item in _items)
        {
            if (item.CompareTo(best) > 0)
            {
                best = item;
            }
        }
        return best;
    }

    public IReadOnlyList<T> Items => _items;
}

// ---------------------------------------------------------------------------
// 2. Constraints that unlock construction
// ---------------------------------------------------------------------------

public interface IEntity
{
    int Id { get; set; }
}

public class Customer : IEntity
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public override string ToString() => $"Customer #{Id} {Name}";
}

public static class Repository
{
    // Three constraints at once: T must implement IEntity, be a reference
    // type, and have a public parameterless constructor so `new T()` works.
    public static T Create<T>(int id) where T : class, IEntity, new()
    {
        return new T { Id = id };
    }
}

// ---------------------------------------------------------------------------
// 3. Variance: `out` = covariant (producer), `in` = contravariant (consumer)
// ---------------------------------------------------------------------------

public abstract class Animal
{
    public string Name { get; init; } = "";
    public override string ToString() => $"{GetType().Name}({Name})";
}

public class Dog : Animal { }
public class Cat : Animal { }

// `out T` means T only ever comes OUT. That makes IProducer<Dog> safely
// usable as IProducer<Animal>: every Dog produced is also an Animal.
public interface IProducer<out T>
{
    T Produce();
}

// `in T` means T only ever goes IN. That makes IConsumer<Animal> usable as
// IConsumer<Dog>: something that handles any Animal certainly handles a Dog.
public interface IConsumer<in T>
{
    string Consume(T item);
}

public class DogBreeder : IProducer<Dog>
{
    public Dog Produce() => new Dog { Name = "Rex" };
}

public class AnimalShelter : IConsumer<Animal>
{
    public string Consume(Animal item) => $"sheltered {item}";
}

public static class Program
{
    // A generic METHOD. T is inferred from the arguments, so callers write
    // Swap(ref a, ref b) rather than Swap<int>(ref a, ref b).
    public static void Swap<T>(ref T left, ref T right)
    {
        (left, right) = (right, left);
    }

    // `notnull` rules out nullable type arguments.
    public static string Describe<T>(T value) where T : notnull
        => $"{typeof(T).Name}: {value}";

    public static void Main()
    {
        Console.WriteLine("-- generic class with a constraint --");
        var numbers = new BoundedList<int>(3);
        foreach (int n in new[] { 5, 9, 2, 7 })
        {
            Console.WriteLine($"  TryAdd({n}) -> {numbers.TryAdd(n)}");
        }
        Console.WriteLine($"  items: [{string.Join(", ", numbers.Items)}], max = {numbers.Max()}");

        Console.WriteLine("-- default(T) differs by kind --");
        Console.WriteLine($"  empty BoundedList<int>.Max()    = {new BoundedList<int>(1).Max()}");
        Console.WriteLine($"  empty BoundedList<string>.Max() = "
                          + (new BoundedList<string>(1).Max() ?? "<null>"));

        Console.WriteLine("-- reified generics --");
        Console.WriteLine($"  typeof(List<int>)    = {typeof(List<int>).Name}");
        Console.WriteLine($"  same as List<string>? {typeof(List<int>) == typeof(List<string>)}");
        // In Java both erase to plain List and this comparison would be true.

        Console.WriteLine("-- new() constraint --");
        Customer customer = Repository.Create<Customer>(42);
        customer.Name = "Ada";
        Console.WriteLine($"  {customer}");

        Console.WriteLine("-- generic method inference --");
        int a = 1, b = 2;
        Swap(ref a, ref b);
        Console.WriteLine($"  after Swap: a={a}, b={b}");
        Console.WriteLine($"  {Describe(7)}");
        Console.WriteLine($"  {Describe("hello")}");

        Console.WriteLine("-- covariance (out) --");
        IProducer<Dog> dogs = new DogBreeder();
        IProducer<Animal> animals = dogs;      // legal ONLY because of `out`
        Console.WriteLine($"  produced {animals.Produce()} via IProducer<Animal>");

        Console.WriteLine("-- contravariance (in) --");
        IConsumer<Animal> shelter = new AnimalShelter();
        IConsumer<Dog> dogShelter = shelter;   // legal ONLY because of `in`
        Console.WriteLine($"  {dogShelter.Consume(new Dog { Name = "Bella" })}");

        Console.WriteLine("-- why IEnumerable is covariant but IList is not --");
        List<Dog> dogList = new() { new Dog { Name = "Rex" }, new Dog { Name = "Bella" } };
        IEnumerable<Animal> readOnly = dogList;  // fine: IEnumerable<out T>
        Console.WriteLine($"  counted {readOnly.Count()} animals through IEnumerable<Animal>");

        // IList<Animal> unsafeList = dogList;   // compile error, and rightly so:
        // if it compiled, you could then do unsafeList.Add(new Cat()), putting
        // a Cat into a List<Dog>. Invariance is what prevents that.
        Console.WriteLine("  IList<T> stays invariant so you cannot Add a Cat to a List<Dog>");
    }
}

/* Expected output:
-- generic class with a constraint --
  TryAdd(5) -> True
  TryAdd(9) -> True
  TryAdd(2) -> True
  TryAdd(7) -> False
  items: [5, 9, 2], max = 9
-- default(T) differs by kind --
  empty BoundedList<int>.Max()    = 0
  empty BoundedList<string>.Max() = <null>
-- reified generics --
  typeof(List<int>)    = List`1
  same as List<string>? False
-- new() constraint --
  Customer #42 Ada
-- generic method inference --
  after Swap: a=2, b=1
  Int32: 7
  String: hello
-- covariance (out) --
  produced Dog(Rex) via IProducer<Animal>
-- contravariance (in) --
  sheltered Dog(Bella)
-- why IEnumerable is covariant but IList is not --
  counted 2 animals through IEnumerable<Animal>
  IList<T> stays invariant so you cannot Add a Cat to a List<Dog>
*/
